# xai_yolo.py

import os
import cv2
import numpy as np
import torch
from ultralytics import YOLO
from pytorch_grad_cam import (
    EigenCAM, EigenGradCAM, GradCAM, GradCAMPlusPlus,
    HiResCAM, LayerCAM, RandomCAM, XGradCAM
)
from pytorch_grad_cam.utils.image import show_cam_on_image, scale_cam_image



# ---------- Helpers ----------
def cam_for_class(model_cam, cam_method, target_layers, t, nc, class_id,
                  eigen_smooth=False, aug_smooth=False):
    # one class → one CAM
    tgt = (lambda raw, c=class_id: yolo_models_target_class(raw, nc, c))
    with torch.enable_grad():
        g = cam_method(model=model_cam,
                       target_layers=target_layers,
                       reshape_transform=reshape_transform)(
            input_tensor=t,
            targets=[tgt],
            eigen_smooth=eigen_smooth,
            aug_smooth=aug_smooth
        )[0]
    return g

def cam_for_class_any_method(
    cam_model: torch.nn.Module,
    method: str,
    target_layers: list[torch.nn.Module],
    t: torch.Tensor,
    nc: int,
    class_id: int | None,
    *,
    eigen_smooth: bool = False,
    aug_smooth: bool = False,
) -> np.ndarray:
    """
    Compute a grayscale CAM (H x W float) for one (method, layers, class_id).
    - For gradient-free methods (Eigen/Random), class_id is ignored.
    - Returns raw grayscale CAM (not scaled/normalized).
    """
    method_cls = CAM_METHODS[method]
    cam = method_cls(model=cam_model, target_layers=target_layers, reshape_transform=reshape_transform)

    if method in _GRAD_FREE:
        g = cam(input_tensor=t, eigen_smooth=eigen_smooth, aug_smooth=aug_smooth)[0]
        return g

    # gradient-based: build targets
    if class_id is None:
        targets = [lambda raw: yolo_models_target_max_class(raw, nc)]
    else:
        targets = [lambda raw, c=class_id: yolo_models_target_class(raw, nc, c)]

    with torch.enable_grad():
        g = cam(input_tensor=t, targets=targets, eigen_smooth=eigen_smooth, aug_smooth=aug_smooth)[0]
    return g


def _draw_boxes_on_rgb(rgb: np.ndarray, xyxy: np.ndarray, cls: np.ndarray, conf: np.ndarray, names) -> np.ndarray:
    out = rgb.copy()
    for (x1,y1,x2,y2), c, p in zip(xyxy.astype(int), cls.astype(int), conf.astype(float)):
        cv2.rectangle(out, (x1,y1), (x2,y2), (255,255,255), 2)
        label = f"{names[c]} {p:.2f}"
        cv2.putText(out, label, (x1, max(0,y1-6)), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,255), 2, cv2.LINE_AA)
    return out

def reshape_transform(act):
    if isinstance(act, (list, tuple)):
        for it in act:
            if torch.is_tensor(it):
                act = it
                break
    assert torch.is_tensor(act)
    if act.ndim == 3:
        act = act.unsqueeze(0)
    elif act.ndim != 4:
        act = act.squeeze()
        assert act.ndim == 4
    return act

def _last_conv_in_block(block: torch.nn.Module):
    last = None
    for m in block.modules():
        if isinstance(m, torch.nn.Conv2d):
            last = m
    return last

def _blocks_to_target_layers(base_model: torch.nn.Module, indices: list[int]):
    """Map user block indices (base_model.model[idx]) -> last Conv2d inside each block."""
    assert hasattr(base_model, "model"), "Expected Ultralytics DetectionModel with `.model`"
    mlist = base_model.model  # nn.ModuleList
    targets = []
    for i in indices:
        if i < 0 or i >= len(mlist):
            print(f"[WARN] layer index {i} out of range [0, {len(mlist)-1}]; skipping.")
            continue
        block = mlist[i]
        conv = _last_conv_in_block(block)
        if conv is None:
            print(f"[WARN] block {i} has no Conv2d; skipping.")
            continue
        targets.append(conv)
    return targets

def pick_two_same_stride_convs(model: torch.nn.Module, imgsz: int, device: str):
    convs = [m for m in model.modules() if isinstance(m, torch.nn.Conv2d)]
    rec, hooks = [], []
    def mk(idx):
        def _h(_m, _i, o):
            t = None
            if torch.is_tensor(o) and o.ndim == 4:
                t = o
            elif isinstance(o, (list, tuple)):
                for it in o:
                    if torch.is_tensor(it) and it.ndim == 4:
                        t = it; break
            if t is not None:
                rec.append((idx, t.shape[-2], t.shape[-1]))
        return _h
    for i, m in enumerate(convs):
        hooks.append(m.register_forward_hook(mk(i)))
    with torch.no_grad():
        _ = model(torch.zeros(1,3,imgsz,imgsz, device=device))
    for h in hooks:
        try: h.remove()
        except: pass
    from collections import defaultdict
    groups = defaultdict(list)
    for idx, h, w in rec:
        groups[(h,w)].append(idx)
    cands = [(h*w,(h,w),idxs) for (h,w),idxs in groups.items() if len(idxs)>=2]
    if not cands:
        # fallback: duplicate last conv
        print("[NOTE] Could not find two Conv2d with same HxW; falling back to duplicating the last conv.")
        return [convs[-1], convs[-1]]
    cands.sort(key=lambda x:x[0], reverse=True)
    _,(H,W),idxs = cands[0]
    print(f"[INFO] Chosen target layers: {idxs[:2]} at {H}x{W}")
    return [convs[idxs[0]], convs[idxs[1]]]

def _to_numpy(x):
    return x.detach().cpu().numpy() if torch.is_tensor(x) else x


class _TensorOutModel(torch.nn.Module):
    def __init__(self, inner): super().__init__(); self.inner=inner
    def forward(self, x):
        y=self.inner(x)
        if isinstance(y,(list,tuple)):
            for it in y:
                if torch.is_tensor(it): y=it; break
            else: y=y[0]
        if y.ndim==2: y=y.unsqueeze(0)
        return y


def yolo_models_target_max_class(raw, nc:int):
    y=raw[0] if isinstance(raw,(list,tuple)) else raw
    if y.ndim==2:y=y.unsqueeze(0)
    B,A,Bc=y.shape; Cexp=4+nc
    if A==Cexp:y=y.transpose(1,2)
    elif Bc!=Cexp:y=y.transpose(1,2);assert y.shape[-1]==Cexp
    return y[...,4:].max()


def yolo_models_target_class(raw, nc:int, c:int):
    y=raw[0] if isinstance(raw,(list,tuple)) else raw
    if y.ndim==2:y=y.unsqueeze(0)
    B,A,Bc=y.shape; Cexp=4+nc
    if A==Cexp:y=y.transpose(1,2)
    elif Bc!=Cexp:y=y.transpose(1,2);assert y.shape[-1]==Cexp
    return y[...,4+c].max()


CAM_METHODS = {
    "EigenCAM":        EigenCAM,
    "EigenGradCAM":    EigenGradCAM,
    "GradCAM":         GradCAM,
    "GradCAMPlusPlus": GradCAMPlusPlus,
    "HiResCAM":        HiResCAM,
    "XGradCAM":        XGradCAM,
    "LayerCAM":        LayerCAM,
    "RandomCAM":       RandomCAM,
}

_GRAD_FREE = {"EigenCAM", "RandomCAM"}

_DEFAULT_LAYERS = {
    "small":  [4, 15],   # 80x80
    "medium": [12, 18],  # 40x40
    "large":  [8, 21],   # 20x20
}

def _build_target_layers(base_model, imgsz, device, method, layer_indices):
    """
    Resolve target layers with user control and safe fallback:
    - If `layer_indices` provided: use last Conv2d from each selected block.
    - If invalid/empty: fall back to auto-pick of 2 same-stride Conv2d.
    - For EigenCAM: ensure >=2 layers (duplicate last if needed) and warn if HxW mismatch.
    """
    min_layers = 2 if method == "EigenCAM" else 1
    targets = []
    if layer_indices:
        targets = _blocks_to_target_layers(base_model, layer_indices)
        if len(targets) < min_layers:
            print(f"[NOTE] Provided layers resolved to {len(targets)} (<{min_layers}); falling back to auto-pick.")
            targets = pick_two_same_stride_convs(base_model, imgsz, device)
    else:
        targets = pick_two_same_stride_convs(base_model, imgsz, device)

    # If EigenCAM and still <2, duplicate last
    if method == "EigenCAM" and len(targets) < 2:
        print("[NOTE] EigenCAM prefers >=2 layers; duplicating the last target.")
        targets = targets + targets[-1:]

    # warn if EigenCAM layers have different spatial size
    if method == "EigenCAM":
        rec = []
        hooks = []
        def mk(m):
            def _h(_m,_i,o):
                t = None
                if torch.is_tensor(o) and o.ndim==4: t=o
                elif isinstance(o,(list,tuple)):
                    for it in o:
                        if torch.is_tensor(it) and it.ndim==4: t=it; break
                if t is not None: rec.append(t.shape[-2:])
            return _h
        with torch.no_grad():
            for m in targets: hooks.append(m.register_forward_hook(mk(m)))
            _ = base_model(torch.zeros(1,3,imgsz,imgsz, device=device))
        for h in hooks:
            try: h.remove()
            except: pass
        if len(rec) >= 2 and any(tuple(rec[0]) != tuple(s) for s in rec[1:]):
            print(f"[WARN] EigenCAM target layers have different HxW: {rec}. Heatmap may be suboptimal.")

    return targets


# ---------- Callable Function ----------
def generate_cam_image(
    weights: str,
    image_path: str,
    output_dir: str,
    method: str = "GradCAMPlusPlus",
    class_id: int | list[int] | None = None,
    imgsz: int = 640,
    device: str = "cuda",
    layer_indices: list[int] | None = None,
    *,
    eigen_smooth: bool = False,
    aug_smooth: bool = False,
    draw_boxes: bool = True,
    conf: float = 0.25,
):
    """
    Generate a CAM overlay for YOLOv8 using chosen method.
    - `layer_indices`: list of indices into base_model.model (ModuleList).
        Each index maps to the block's last Conv2d as the CAM target layer.
        If None/invalid: falls back to auto-pick of two same-stride Conv2d.
    """
    device = device if device in {"cuda","cpu"} else ("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs(output_dir, exist_ok=True)

    yolo = YOLO(weights)
    base_model = yolo.model.to(device).eval()
    for p in base_model.parameters(): p.requires_grad_(True)
    names = yolo.names; nc=len(names)

    bgr = cv2.imread(image_path)
    assert bgr is not None, f"Cannot read image: {image_path}"
    bgr = cv2.resize(bgr, (imgsz,imgsz))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32)/255.0
    t = torch.from_numpy(rgb.transpose(2,0,1))[None].to(device)
    

    cam_model = _TensorOutModel(base_model).eval()
    target_layers = _build_target_layers(base_model, imgsz, device, method, layer_indices)

    method_cls = CAM_METHODS[method]
    cam = method_cls(model=cam_model, target_layers=target_layers, reshape_transform=reshape_transform)

    grad_free = method in {"EigenCAM","RandomCAM"}
    if grad_free:
        # gradient-free methods ignore targets
        grayscale = cam(
            input_tensor=t,
            eigen_smooth=eigen_smooth,
            aug_smooth=aug_smooth
        )[0]
    else:
        # normalize class_id to a list of class indices (or None)
        if class_id is None:
            targets = [lambda raw: yolo_models_target_max_class(raw, nc)]
        else:
            class_ids = class_id if isinstance(class_id, (list, tuple)) else [class_id]
            targets = [
                (lambda raw, c=cid: yolo_models_target_class(raw, nc, c))
                for cid in class_ids
            ]

        with torch.enable_grad():
            grayscale = cam(
                input_tensor=t,
                targets=targets,
                eigen_smooth=eigen_smooth,
                aug_smooth=aug_smooth
            )[0]

    overlay = show_cam_on_image(rgb, scale_cam_image(grayscale), use_rgb=True)

    # ---- FN fallback + box drawing ----
    results = YOLO(weights).predict(source=bgr, imgsz=imgsz, conf=conf, verbose=False)[0]
    has_boxes = getattr(results, "boxes", None) is not None and len(results.boxes) > 0

    if not has_boxes and class_id is None and method not in {"EigenCAM","RandomCAM"}:
        print("[NOTE] No detections; using global-max class CAM already computed.")
    if not has_boxes and class_id is not None and method not in {"EigenCAM","RandomCAM"}:
        print(f"[NOTE] No detections; used class-specific CAM for class_id={class_id}.")

    if draw_boxes and has_boxes:
        xyxy = _to_numpy(results.boxes.xyxy)
        cls  = _to_numpy(results.boxes.cls)
        confs = _to_numpy(results.boxes.conf)
        overlay = _draw_boxes_on_rgb(overlay, xyxy, cls, confs, names)

    # Save
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_path = os.path.join(output_dir, f"{base}.png")
    cv2.imwrite(out_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    print(f"[OK] Saved CAM: {out_path}")
    return out_path


def generate_cam_fused_classes(
    weights: str,
    image_path: str,
    output_dir: str,
    entries: list[dict],
    *,
    imgsz: int = 640,
    device: str = "cuda",
    draw_boxes: bool = True,
    conf: float = 0.25,
    eigen_smooth: bool = False,
    aug_smooth: bool = False,
    fuse: str = "max",  # "max" or "sum"
):
    """
    entries: list of dicts, each like:
        {
          "class_id": 9,                          # or None (global max for grad-based; ignored for grad-free)
          "method": "HiResCAM",                   # any of CAM_METHODS
          "layer_indices": [15],                  # explicit list of block indices (preferred)
          # OR:
          "scale": "small" | "medium" | "large",  # optional convenience if layer_indices not given
          "weight": 1.0                           # optional fusion weight
        }
    """
    device = device if device in {"cuda", "cpu"} else ("cuda" if torch.cuda.is_available() else "cpu")
    os.makedirs(output_dir, exist_ok=True)

    # Load model once
    yolo = YOLO(weights)
    base_model = yolo.model.to(device).eval()
    for p in base_model.parameters(): p.requires_grad_(True)
    names = yolo.names; nc = len(names)

    # Preprocess once
    bgr = cv2.imread(image_path); assert bgr is not None, f"Cannot read {image_path}"
    bgr = cv2.resize(bgr, (imgsz, imgsz))
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
    t = torch.from_numpy(rgb.transpose(2, 0, 1))[None].to(device)

    # CAM model wrapper
    cam_model = _TensorOutModel(base_model).eval()

    # Accumulator
    fused = None

    # Compute each entry CAM and fuse
    for e in entries:
        method = e["method"]
        class_id = e.get("class_id", None)
        weight = float(e.get("weight", 1.0))

        # Resolve target layers
        li = e.get("layer_indices", None)
        if li is None and "scale" in e:
            scale = e["scale"]
            li = _DEFAULT_LAYERS.get(scale, None)
            if li is None:
                print(f"[WARN] Unknown scale '{scale}', falling back to auto-pick.")
        target_layers = _build_target_layers(base_model, imgsz, device, method, li)

        # Compute grayscale CAM
        g = cam_for_class_any_method(
            cam_model, method, target_layers, t, nc, class_id,
            eigen_smooth=eigen_smooth, aug_smooth=aug_smooth,
        )

        # Normalize to [0,1] for stable fusion
        m = scale_cam_image(g)

        # Weighted fuse
        m_w = m * weight
        fused = m_w if fused is None else (np.maximum(fused, m_w) if fuse == "max" else fused + m_w)

    # Overlay
    overlay = show_cam_on_image(rgb, np.clip(fused, 0, 1), use_rgb=True)

    # Optional detection boxes on the overlay
    if draw_boxes:
        det = yolo.predict(source=bgr, imgsz=imgsz, conf=conf, verbose=False)[0]
        if getattr(det, "boxes", None) is not None and len(det.boxes) > 0:
            xyxy = _to_numpy(det.boxes.xyxy); cls = _to_numpy(det.boxes.cls); confs = _to_numpy(det.boxes.conf)
            overlay = _draw_boxes_on_rgb(overlay, xyxy, cls, confs, names)

    # Save
    base = os.path.splitext(os.path.basename(image_path))[0]
    out_path = os.path.join(output_dir, f"{base}.png")
    cv2.imwrite(out_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
    print(f"[OK] Saved fused CAM: {out_path}")
    return out_path
