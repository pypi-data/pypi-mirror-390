# xai_shap.py

from pathlib import Path
from typing import List, Optional, Tuple
import numpy as np
import cv2
import matplotlib.pyplot as plt
import shap
from ultralytics import YOLO
from functools import lru_cache


# ----------------------------
# Utilities
# ----------------------------
def load_image_bgr(path: str, max_side: int = 1024) -> np.ndarray:
    """Load image (BGR uint8). Resize so the longer side <= max_side."""
    img = cv2.imread(path, cv2.IMREAD_COLOR)
    if img is None:
        raise FileNotFoundError(path)
    h, w = img.shape[:2]
    scale = min(1.0, max_side / max(h, w))
    if scale < 1.0:
        img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_AREA)
    return img


def bgr_to_rgb_float(img_bgr: np.ndarray) -> np.ndarray:
    """BGR uint8 -> RGB float32 in [0,255]."""
    img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32)
    return img_rgb


def _iou_xyxy(a: np.ndarray, b: np.ndarray) -> float:
    """IoU for boxes in [x1,y1,x2,y2] format."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    inter_x1 = max(ax1, bx1)
    inter_y1 = max(ay1, by1)
    inter_x2 = min(ax2, bx2)
    inter_y2 = min(ay2, by2)
    iw = max(0.0, inter_x2 - inter_x1)
    ih = max(0.0, inter_y2 - inter_y1)
    inter = iw * ih
    area_a = max(0.0, (ax2 - ax1)) * max(0.0, (ay2 - ay1))
    area_b = max(0.0, (bx2 - bx1)) * max(0.0, (by2 - by1))
    denom = area_a + area_b - inter + 1e-6
    return float(inter / denom)


# ------------------------------------------------------
# YOLO → scalar scoring wrapper for a specific detection
# ------------------------------------------------------
class YoloDetectionScoreWrapper:
    """
    Black-box scorer for a *specific detection*:
      image -> scalar score (confidence) for the detection matching (class_id + IoU to ref_box).
    If no matching box is found above the IoU threshold, returns 0.0 for that image.
    """

    def __init__(
        self,
        yolo: YOLO,
        *,
        class_id: int,
        ref_box_xyxy: np.ndarray,      # shape (4,), in [x1,y1,x2,y2], original image coords
        iou_match_threshold: float = 0.5,
        imgsz: int = 640,
        device: Optional[str] = None,
    ):
        self.yolo = yolo
        self.class_id = int(class_id)
        self.ref_box = ref_box_xyxy.astype(float)
        self.iou_thr = float(iou_match_threshold)
        self.imgsz = imgsz
        self.device = device

    def __call__(self, X: np.ndarray) -> np.ndarray:
        """
        X: (N, H, W, 3), RGB float32 in [0,255].
        Returns: (N,) vector of confidences for the matching detection.
        """
        batch = []
        for i in range(X.shape[0]):
            rgb = X[i].astype(np.uint8)
            bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
            batch.append(bgr)

        results = self.yolo.predict(
            batch, imgsz=self.imgsz, device=self.device, verbose=False, save=False
        )

        out_scores = []
        for res in results:
            score = 0.0
            if getattr(res, "boxes", None) is not None and len(res.boxes) > 0:
                cls = res.boxes.cls.detach().cpu().numpy().astype(int)
                conf = res.boxes.conf.detach().cpu().numpy().astype(float)
                xyxy = res.boxes.xyxy.detach().cpu().numpy().astype(float)  # (N,4)

                # Filter by class and find the one with max IoU to our ref_box
                mask = (cls == self.class_id)
                if mask.any():
                    cand_xyxy = xyxy[mask]
                    cand_conf = conf[mask]
                    # compute IoU for candidates
                    ious = np.array([_iou_xyxy(b, self.ref_box) for b in cand_xyxy], dtype=float)
                    best_idx = int(ious.argmax())
                    best_iou = float(ious[best_idx])
                    if best_iou >= self.iou_thr:
                        score = float(cand_conf[best_idx])
            out_scores.append(score)

        return np.array(out_scores, dtype=np.float32)


# ------------------------------------------------------
# Cached per-shape masker (optimization)
# ------------------------------------------------------
@lru_cache(maxsize=8)
def _get_masker(h: int, w: int):
    # SHAP ≥0.45: shape must be specified when mask_value is a string.
    return shap.maskers.Image("inpaint_telea", shape=(h, w, 3))


# ------------------------------------------------------
# API
# ------------------------------------------------------
def SHAP(
    images_dir: str,
    *,
    weights: str = "YOLOx.pt",
    output_dir: str = "./shap_out",
    imgsz: int = 640,
    device: Optional[str] = None,
    max_side: int = 1024,
    nsamples: int = 300,
    iou_match_threshold: float = 0.5,
    max_detections_per_image: Optional[int] = None,  # None = all
) -> List[str]:
    """
    Compute SHAP attributions for *each detection* produced by YOLOx in every image.

    For each detection (class_id, box), we:
      1) Build a scorer that returns the confidence of that specific detection (via IoU matching).
      2) Run SHAP with an image masker to get per-pixel attributions.
      3) Save one PNG per detection with the reference box drawn for context.

    Returns:
        List of saved PNG file paths.

    Notes:
      - Runtime grows with the number of detections; consider `max_detections_per_image`.
      - `iou_match_threshold` controls identity matching under perturbations (default 0.5).
    """
    images_path = Path(images_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    yolo = YOLO(weights)
    names = yolo.names  # {id: class_name}

    jpgs = sorted([p for p in images_path.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if not jpgs:
        raise RuntimeError(f"No JPG/PNG found under {images_path}")

    saved: List[str] = []

    for img_path in jpgs:
        # Load & prep image
        bgr = load_image_bgr(str(img_path), max_side=max_side)
        rgb = bgr_to_rgb_float(bgr)  # (H,W,3)
        H, W = rgb.shape[:2]

        # Run YOLO once to get reference detections on the *unmasked* image
        base_res = yolo.predict(
            rgb.astype(np.uint8)[:, :, ::-1], imgsz=imgsz, device=device, verbose=False, save=False
        )

        if not base_res or getattr(base_res[0], "boxes", None) is None or len(base_res[0].boxes) == 0:
            print(f"[INFO] No detections in {img_path.name}; skipping.")
            continue

        # Extract detections: (class_id, conf, xyxy)
        cls_all = base_res[0].boxes.cls.detach().cpu().numpy().astype(int)
        conf_all = base_res[0].boxes.conf.detach().cpu().numpy().astype(float)
        xyxy_all = base_res[0].boxes.xyxy.detach().cpu().numpy().astype(float)
        det_indices = list(range(len(cls_all)))

        # Optionally sort by confidence and cap count
        det_indices.sort(key=lambda i: conf_all[i], reverse=True)
        if max_detections_per_image is not None:
            det_indices = det_indices[:max_detections_per_image]

        # Prepare per-image masker
        masker = _get_masker(H, W)

        # Make a subfolder for this image’s outputs (optional but tidy)
        per_image_dir = out_path / img_path.stem
        per_image_dir.mkdir(parents=True, exist_ok=True)

        for d_idx in det_indices:
            class_id = int(cls_all[d_idx])
            class_name = names.get(class_id, str(class_id))
            ref_conf = float(conf_all[d_idx])
            ref_box = xyxy_all[d_idx]  # [x1,y1,x2,y2]

            # Build scorer for this *specific detection*
            scorer = YoloDetectionScoreWrapper(
                yolo,
                class_id=class_id,
                ref_box_xyxy=ref_box,
                iou_match_threshold=iou_match_threshold,
                imgsz=imgsz,
                device=device,
            )

            # SHAP explainer and attribution
            explainer = shap.Explainer(scorer, masker, algorithm="auto")
            X = np.expand_dims(rgb, axis=0)  # (1,H,W,3)
            shap_values = explainer(X, max_evals=nsamples)

            # Plot & save (overlay the reference box for context)
            shap.plots.image(shap_values[0], show=False)


            fig = plt.gcf()
            axs = fig.axes

            if len(axs) >= 2:
                ax_left = axs[0]
                ax_left.clear()
                ax_left.imshow(rgb.astype(np.uint8))
                ax_left.axis("off")

            # Draw the reference box
            x1, y1, x2, y2 = ref_box
            ax = plt.gca()
            rect = plt.Rectangle(
                (x1, y1),
                (x2 - x1),
                (y2 - y1),
                fill=False,
                linewidth=2.0,
            )
            ax.add_patch(rect)
            ax.text(
                x1,
                max(0, y1 - 5),
                f"{class_name} {ref_conf:.2f}",
                fontsize=9,
                bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=1.5),
            )

            outfile = per_image_dir / f"{img_path.stem}__det{d_idx:02d}__{class_name}_{ref_conf:.2f}.png"
            plt.title(f"SHAP (per-box) — {class_name}  conf={ref_conf:.2f}")
            plt.savefig(str(outfile), bbox_inches="tight", dpi=200)
            plt.close()
            print(f"[OK] Saved {outfile}")
            saved.append(str(outfile))

    print("Done.")
    return saved