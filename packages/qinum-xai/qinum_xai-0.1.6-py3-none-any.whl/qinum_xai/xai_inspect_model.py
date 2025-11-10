# xai_inspect_model.py
import torch
from ultralytics import YOLO

def _last_conv_in_block(block: torch.nn.Module):
    last = None
    for m in block.modules():
        if isinstance(m, torch.nn.Conv2d):
            last = m
    return last

def inspect_yolo_blocks(weights: str, imgsz: int = 640, device: str = "cuda"):
    """
    Print a concise table of Ultralytics YOLOv8 blocks (base_model.model[i]) with:
      - block index (i)
      - block type
      - output feature map size (H x W) for a dummy imgsz x imgsz input
      - number of Conv2d modules inside the block
      - whether it has a Conv2d and the repr() of the last Conv2d

    Returns: list of dict records for programmatic use.
    """
    device = device if device in {"cuda", "cpu"} else ("cuda" if torch.cuda.is_available() else "cpu")
    yolo = YOLO(weights)
    model = yolo.model.to(device).eval()
    assert hasattr(model, "model"), "Expected Ultralytics DetectionModel with `.model`"
    blocks = model.model  # nn.ModuleList

    # forward hooks to capture block outputs and conv counts
    records = [{"idx": i, "type": type(b).__name__, "H": None, "W": None,
                "n_convs": 0, "has_conv": False, "last_conv": None} for i, b in enumerate(blocks)]
    hooks = []

    def make_block_hook(i):
        def _h(_m, _inp, out):
            # normalize to BCHW tensor if possible
            t = None
            if torch.is_tensor(out) and out.ndim == 4:
                t = out
            elif isinstance(out, (list, tuple)):
                for it in out:
                    if torch.is_tensor(it) and it.ndim == 4:
                        t = it
                        break
            if t is not None:
                H, W = int(t.shape[-2]), int(t.shape[-1])
                records[i]["H"], records[i]["W"] = H, W
        return _h

    def count_convs(block):
        n = 0
        for m in block.modules():
            if isinstance(m, torch.nn.Conv2d):
                n += 1
        return n

    # register hooks and conv stats
    for i, b in enumerate(blocks):
        hooks.append(b.register_forward_hook(make_block_hook(i)))
        records[i]["n_convs"] = count_convs(b)
        conv = _last_conv_in_block(b)
        if conv is not None:
            records[i]["has_conv"] = True
            records[i]["last_conv"] = repr(conv)

    # run a single dummy forward to materialize HxW
    with torch.no_grad():
        _ = model(torch.zeros(1, 3, imgsz, imgsz, device=device))

    for h in hooks:
        try:
            h.remove()
        except:
            pass

    # pretty print
    print("—— YOLO Blocks (indexable for CAM) ——")
    print(f"{'idx':>3}  {'type':<20}  {'HxW':>12}  {'#Conv':>5}  {'hasConv':>7}")
    for r in records:
        hw = f"{r['H']}x{r['W']}" if (r["H"] and r["W"]) else "n/a"
        print(f"{r['idx']:>3}  {r['type']:<20}  {hw:>12}  {r['n_convs']:>5}  {str(r['has_conv']):>7}")
    print("—— Groups by spatial size (useful for P3/P4/P5) ——")
    from collections import defaultdict
    groups = defaultdict(list)
    for r in records:
        if r["H"] and r["W"]:
            groups[(r["H"], r["W"])].append(r["idx"])
    # sort groups by area desc (largest HxW first)
    groups_sorted = sorted(groups.items(), key=lambda kv: kv[0][0]*kv[0][1], reverse=True)
    for (H, W), idxs in groups_sorted:
        print(f"  • {H}x{W}: indices {idxs}")

    return records
