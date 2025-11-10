#xai_lime.py

from pathlib import Path
from typing import List, Optional
import numpy as np
import cv2
import matplotlib.pyplot as plt
from functools import lru_cache

from ultralytics import YOLO
from lime.lime_image import LimeImageExplainer
from skimage.segmentation import slic


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


def bgr_to_rgb_uint8(img_bgr: np.ndarray) -> np.ndarray:
    """BGR uint8 -> RGB uint8."""
    return cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)


def _iou_xyxy(a: np.ndarray, b: np.ndarray) -> float:
    """IoU for boxes in [x1,y1,x2,y2]."""
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
# Detection-specific classifier_fn for LIME
# ------------------------------------------------------
class LimeYoloDetectionClassifier:
    """
    A binary classifier_fn for LIME tied to ONE reference detection:
    Given perturbed images, return a 2-column array [[p_not, p_target], ...]
    where p_target ≈ confidence of the best IoU-matched box of the same class,
    and p_not = 1 - p_target (clipped).

    Notes:
      - LIME expects probabilities; we map YOLO confidence ∈ [0,1] to [1-conf, conf].
      - If no matching box (IoU < threshold), p_target = 0.
    """

    def __init__(
        self,
        yolo: YOLO,
        *,
        class_id: int,
        ref_box_xyxy: np.ndarray,
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

    def __call__(self, images: np.ndarray) -> np.ndarray:
        """
        images: list/array of RGB uint8 arrays (H, W, 3) from LIME’s perturbations.
        Return: np.ndarray of shape (N, 2) with [p_not, p_target].
        """

        batch_bgr = [cv2.cvtColor(img.astype(np.uint8), cv2.COLOR_RGB2BGR) for img in images]

        results = self.yolo.predict(
            batch_bgr, imgsz=self.imgsz, device=self.device, verbose=False, save=False
        )

        outputs = []
        for res in results:
            p_target = 0.0
            if getattr(res, "boxes", None) is not None and len(res.boxes) > 0:
                cls = res.boxes.cls.detach().cpu().numpy().astype(int)
                conf = res.boxes.conf.detach().cpu().numpy().astype(float)
                xyxy = res.boxes.xyxy.detach().cpu().numpy().astype(float)

                mask = (cls == self.class_id)
                if mask.any():
                    cand_xyxy = xyxy[mask]
                    cand_conf = conf[mask]
                    ious = np.array([_iou_xyxy(b, self.ref_box) for b in cand_xyxy], dtype=float)
                    best_idx = int(ious.argmax())
                    best_iou = float(ious[best_idx])
                    if best_iou >= self.iou_thr:
                        p_target = float(np.clip(cand_conf[best_idx], 0.0, 1.0))

            outputs.append([1.0 - p_target, p_target])

        return np.array(outputs, dtype=np.float32)


# ------------------------------------------------------
# Cached explainer (LIME is light, but reuse is fine)
# ------------------------------------------------------
@lru_cache(maxsize=1)
def _get_lime_explainer():
    return LimeImageExplainer()


# ------------------------------------------------------
# Public API
# ------------------------------------------------------
def lime(
    images_dir: str,
    *,
    weights: str = "YOLOx.pt",
    output_dir: str = "./lime_out_per_box",
    imgsz: int = 640,
    device: Optional[str] = None,
    max_side: int = 1024,
    iou_match_threshold: float = 0.5,
    max_detections_per_image: Optional[int] = None,   # cap to control runtime
    num_samples: int = 1000,                          # LIME perturbation budget (↑ for fidelity)
    segmentation_num_segments: int = 300,             # SLIC superpixels
    segmentation_compactness: float = 10.0,
    segmentation_sigma: float = 1.0,
    positive_only: bool = False,                      # show both positive and negative regions
    num_features: int = 10,                           # top superpixels to highlight
    hide_rest: bool = False,                          # False = overlay on original
) -> List[str]:
    """
    Compute LIME attributions for *each detection* produced by YOLOx in every image.

    Returns:
        List of saved PNG file paths.
    """
    images_path = Path(images_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    yolo = YOLO(weights)
    names = yolo.names  # {id: class_name}

    jpgs = sorted([p for p in images_path.iterdir() if p.suffix.lower() in (".jpg", ".jpeg", ".png")])
    if not jpgs:
        raise RuntimeError(f"No JPG/PNG found under {images_path}")

    explainer = _get_lime_explainer()
    saved: List[str] = []

    for img_path in jpgs:
        bgr = load_image_bgr(str(img_path), max_side=max_side)
        rgb = bgr_to_rgb_uint8(bgr)
        H, W = rgb.shape[:2]

        # Get base detections
        base_res = yolo.predict(
            bgr, imgsz=imgsz, device=device, verbose=False, save=False
        )
        if not base_res or getattr(base_res[0], "boxes", None) is None or len(base_res[0].boxes) == 0:
            print(f"[INFO] No detections in {img_path.name}; skipping.")
            continue

        cls_all = base_res[0].boxes.cls.detach().cpu().numpy().astype(int)
        conf_all = base_res[0].boxes.conf.detach().cpu().numpy().astype(float)
        xyxy_all = base_res[0].boxes.xyxy.detach().cpu().numpy().astype(float)
        det_indices = list(range(len(cls_all)))

        # Sort by confidence
        det_indices.sort(key=lambda i: conf_all[i], reverse=True)
        if max_detections_per_image is not None:
            det_indices = det_indices[:max_detections_per_image]

        # Subfolder per image
        per_image_dir = out_path / img_path.stem
        per_image_dir.mkdir(parents=True, exist_ok=True)

        # Pre-build SLIC segmentation (deterministic across runs)
        def segmentation_fn(x):
            # x is RGB uint8 image (H,W,3)
            # Return a 2D array of superpixel labels
            return slic(
                x,
                n_segments=segmentation_num_segments,
                compactness=segmentation_compactness,
                sigma=segmentation_sigma,
                start_label=0,
            )

        for d_idx in det_indices:
            class_id = int(cls_all[d_idx])
            class_name = names.get(class_id, str(class_id))
            ref_conf = float(conf_all[d_idx])
            ref_box = xyxy_all[d_idx]

            # Detection-specific classifier_fn
            classifier_fn = LimeYoloDetectionClassifier(
                yolo,
                class_id=class_id,
                ref_box_xyxy=ref_box,
                iou_match_threshold=iou_match_threshold,
                imgsz=imgsz,
                device=device,
            )

            base_probs = classifier_fn(np.expand_dims(rgb, axis=0))[0]



            explanation = explainer.explain_instance(
                image=rgb,
                classifier_fn=classifier_fn,
                labels=[1],
                hide_color=0,
                num_samples=num_samples,
                segmentation_fn=segmentation_fn,
            )


            label_to_show = 1 if 1 in explanation.local_exp else explanation.top_labels[0]

            lime_img, lime_mask = explanation.get_image_and_mask(
                label=label_to_show,
                positive_only=positive_only,
                num_features=num_features,
                hide_rest=hide_rest,
            )


            # Draw reference box on top of the LIME visualization
            fig = plt.figure(figsize=(8, 6))
            plt.imshow(lime_img)
            x1, y1, x2, y2 = ref_box
            ax = plt.gca()
            rect = plt.Rectangle(
                (x1, y1), (x2 - x1), (y2 - y1),
                fill=False, linewidth=2.0
            )
            ax.add_patch(rect)
            ax.text(
                x1, max(0, y1 - 5),
                f"{class_name} {ref_conf:.2f}",
                fontsize=9,
                bbox=dict(facecolor="white", alpha=0.6, edgecolor="none", pad=1.0),
            )

            outfile = per_image_dir / f"{img_path.stem}__det{d_idx:02d}__{class_name}_{ref_conf:.2f}.png"
            plt.title(f"LIME (per-box) — {class_name}  conf={ref_conf:.2f}")
            plt.axis("off")
            plt.tight_layout()
            plt.savefig(str(outfile), bbox_inches="tight", dpi=200)
            plt.close(fig)
            print(f"[OK] Saved {outfile}")
            saved.append(str(outfile))

    print("Done.")
    return saved