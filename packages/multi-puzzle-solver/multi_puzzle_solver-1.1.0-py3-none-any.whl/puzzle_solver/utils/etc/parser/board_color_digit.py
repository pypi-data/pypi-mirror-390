from pathlib import Path
from functools import lru_cache
import numpy as np
from PIL import Image

cv2 = None
plt = None


DIGITS_DIR = Path(__file__).parent / "digits"


# ------------------------------------------------------------------
# helpers
# ------------------------------------------------------------------
def cluster_positions(lines, axis=0, tol=3):
    """Group nearly identical x (or y) positions into one line."""
    pts = []
    for x1, y1, x2, y2 in lines:
        pts.append(x1 if axis == 0 else y1)
    pts = sorted(pts)
    groups = []
    current = [pts[0]]
    for p in pts[1:]:
        if abs(p - current[-1]) <= tol:
            current.append(p)
        else:
            groups.append(current)
            current = [p]
    groups.append(current)
    return [int(np.mean(g)) for g in groups]



def detect_color_simple(cell_bgr):
    """Roughly decide whether the cell text is orange, yellow or black."""
    hsv = cv2.cvtColor(cell_bgr, cv2.COLOR_BGR2HSV)
    h = hsv[:, :, 0]
    s = hsv[:, :, 1]
    v = hsv[:, :, 2]
    # print(f'H: {h}')
    # print(f'S: {s}')
    # print(f'V: {v}')

    mask = (h != 0) | (s != 0) | (v != 255)
    if not np.any(mask):
        return None

    mh = int(np.mean(h[mask]))
    ms = int(np.mean(s[mask]))
    mv = int(np.mean(v[mask]))
    # print('masked %: ', np.sum(mask) / mask.size * 100)

    return (mh, ms, mv)

















































def normalize_cell(img_bgr, size=28):
    """
    Take a BGR cell image, make it grayscale, binarize, and resize to a fixed size.
    Returns a 2D uint8 array (0 or 255).
    """
    gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

    # light background / dark text is common, so threshold with OTSU
    # blur a bit first
    _, bw = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Sometimes text becomes white on black, sometimes black on white.
    # Let's make "ink" be black (0) and background be white (255).
    # Heuristic: if the mean is low, invert.
    if bw.mean() < 127:
        bw = 255 - bw

    # resize to fixed size
    bw_resized = cv2.resize(bw, (size, size), interpolation=cv2.INTER_AREA)

    return bw_resized


@lru_cache(maxsize=1)
def _load_digit_templates(size=28):
    """
    Load all images from ./digits/ and normalize them to the same shape.
    Returns list of (name_without_ext, normalized_image, full_path).
    Cached so we don’t reload every call — but if we add new digits,
    we can clear the cache.
    """
    entries = []
    for p in DIGITS_DIR.iterdir():
        if not p.is_file():
            continue
        if p.suffix.lower() not in [".png", ".jpg", ".jpeg", ".bmp"]:
            continue
        img = cv2.imread(str(p), cv2.IMREAD_GRAYSCALE)
        if img is None:
            continue
        digit = int(p.stem.split("_")[0])
        # ensure same size / format
        if img.shape != (size, size):
            img = cv2.resize(img, (size, size), interpolation=cv2.INTER_AREA)
        entries.append((digit, img, p))
    return entries


def _save_digit_image(norm_img, label, size=28):
    """
    Save normalized img to ./digits/ as `{label}.png`.
    If file exists, append a counter.
    """
    label = str(label).strip()
    out_path = DIGITS_DIR / f"{label}.png"
    if out_path.exists():
        # find a free name like label_1.png, label_2.png, ...
        i = 1
        while True:
            cand = DIGITS_DIR / f"{label}_{i}.png"
            if not cand.exists():
                out_path = cand
                break
            i += 1

    cv2.imwrite(str(out_path), norm_img)
    # refresh cache since we added a new file
    _load_digit_templates.cache_clear()
    return out_path


def classify_digit(cell_bgr, visualize=False, size=28, dist_thresh=500):
    """
    1. normalize the cell
    2. compare pixel-wise to files in ./digits/
    3. if close enough -> return that filename (digit)
    4. else -> ask user in terminal, save, return label

    Returns the recognized digit as string.
    """
    norm = normalize_cell(cell_bgr, size=size)

    # load templates
    templates = _load_digit_templates(size=size)

    best_label = None
    best_dist = float("inf")

    if templates:
        for label, tmpl_img, _ in templates:
            # simple pixel-wise L1 distance
            dist = np.sum(np.abs(norm.astype(np.int16) - tmpl_img.astype(np.int16)))
            if dist < best_dist:
                best_dist = dist
                best_label = label

        # if it's close enough, accept
        if best_dist <= dist_thresh:
            return best_label

    # otherwise we need user input
    if visualize:
        print(f"Unknown digit encountered., best_label: {best_label}, best_dist: {best_dist}, dist_thresh: {dist_thresh}")
        show_wait_destroy("unknown digit", norm)

    print("\n[Digit classifier] Unknown digit encountered.")
    print(f"Best match dist = {best_dist:.0f} (threshold={dist_thresh}), so asking user.")
    user_label = input("Enter the digit/label for this cell (e.g. 0-9 or letter): ").strip()
    if not user_label:
        user_label = "unknown"

    saved_path = _save_digit_image(norm, user_label, size=size)
    print(f"Saved new digit template to: {saved_path}")

    return user_label


def show_wait_destroy(winname, img):
    cv2.imshow(winname, img)
    cv2.moveWindow(winname, 500, 1000)
    cv2.waitKey(0)
    cv2.destroyWindow(winname)



def cluster_triplets(
        triplets,
        k_min=2,
        k_max=8,
        dim_reduce="pca",
        random_state=42,
        show_plot=True,):
    from sklearn.cluster import KMeans
    from sklearn.decomposition import PCA
    from sklearn.manifold import TSNE

    X = np.array(triplets, dtype=float)
    n_samples = X.shape[0]
    k_max = min(k_max, n_samples)
    ks = list(range(k_min, k_max + 1))

    sse = []
    kmeans_models = {}
    for k in ks:
        km = KMeans(n_clusters=k, n_init="auto", random_state=random_state)
        km.fit(X)
        sse.append(km.inertia_)
        kmeans_models[k] = km

    x1, y1 = ks[0], sse[0]
    x2, y2 = ks[-1], sse[-1]
    distances = []
    for x, y in zip(ks, sse):
        num = abs((y2 - y1) * x - (x2 - x1) * y + x2*y1 - y2*x1)
        den = np.sqrt((y2 - y1)**2 + (x2 - x1)**2)
        distances.append(num / den)

    best_idx = int(np.argmax(distances))
    best_k = ks[best_idx]
    best_model = kmeans_models[best_k]
    labels = best_model.labels_

    if show_plot:
        if dim_reduce.lower() == "tsne":
            reducer = TSNE(n_components=2, random_state=random_state, init="pca")
            X_2d = reducer.fit_transform(X)
        else:
            reducer = PCA(n_components=2, random_state=random_state)
            X_2d = reducer.fit_transform(X)
        plt.figure(figsize=(6, 5))
        scatter = plt.scatter(
            X_2d[:, 0], X_2d[:, 1],
            c=labels,
            s=50
        )
        plt.title(f"Clusters (k={best_k})")
        plt.xlabel("Component 1")
        plt.ylabel("Component 2")
        plt.colorbar(scatter, label="Cluster")
        plt.tight_layout()
        plt.show()

    return labels, best_k



def parse_board(image_path):
    """Main function: detects grid, loops through cells, returns 2D array."""
    global cv2, plt
    
    VISUALIZE_LINES = False
    
    import cv2
    import matplotlib.pyplot as plt
    assert image_path.exists(), f"Image file does not exist: {image_path}"
    if image_path.suffix.lower() == '.pdf':
        image_bgr = pdf_to_cv_img(image_path)
    else:
        image_bgr = cv2.imread(image_path)
    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150, apertureSize=3)
    if VISUALIZE_LINES:
        show_wait_destroy("edges", edges)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=80, minLineLength=150, maxLineGap=5)
    vert, horiz = [], []
    for l in lines:
        x1, y1, x2, y2 = l[0]
        if abs(x1 - x2) < 5:
            vert.append((x1, y1, x2, y2))
        elif abs(y1 - y2) < 5:
            horiz.append((x1, y1, x2, y2))

    # add_borders = False
    add_borders = True
    clip_ends = False
    # clip_ends = True

    x_lines = cluster_positions(vert, axis=0, tol=3)
    y_lines = cluster_positions(horiz, axis=1, tol=3)
    if add_borders:
        x_lines = [0] + x_lines + [image_bgr.shape[1]]
        y_lines = [0] + y_lines + [image_bgr.shape[0]]
    if clip_ends:
        x_lines = x_lines[1:-1]
        y_lines = y_lines[1:-1]
    print(f"x_lines: {x_lines}")
    print(f"y_lines: {y_lines}")
    # visualize the lines
    if VISUALIZE_LINES:
        for x in x_lines:
            cv2.line(image_bgr, (x, 0), (x, image_bgr.shape[0]), (0, 0, 255), 2)
        for y in y_lines:
            cv2.line(image_bgr, (0, y), (image_bgr.shape[1], y), (0, 0, 255), 2)
        show_wait_destroy("image_bgr", image_bgr)

    n_rows = len(y_lines) - 1
    n_cols = len(x_lines) - 1
    colors = []
    cell_ri_ci = []
    digit_ri_ci = []
    for ri in range(n_rows):
        print('--------------------------------')
        print(f'row: {ri}')
        for ci in range(n_cols):
            print(f'percentage complete: {(ri * n_cols + ci) / (n_rows * n_cols):.1%}')
            # print(f"ri: {ri}, ci: {ci}")
            y1, y2 = y_lines[ri], y_lines[ri + 1]
            x1, x2 = x_lines[ci], x_lines[ci + 1]
            if y2 - y1 <= 0 or x2 - x1 <= 0:
                continue
            cell = image_bgr[y1:y2, x1:x2]

            # make a mask for “anything that looks like text”
            hsv = cv2.cvtColor(cell, cv2.COLOR_BGR2HSV)
            s = hsv[:, :, 1]
            v = hsv[:, :, 2]
            mask = ((s > 20) | (v < 210)).astype(np.uint8) * 255
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, np.ones((2, 2), np.uint8), iterations=1)

            cnts, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cell_area = cell.shape[0] * cell.shape[1]

            parts = []
            for c in cnts:
                x, y, wc, hc = cv2.boundingRect(c)
                # print(f"x: {x}, y: {y}, wc: {wc}, hc: {hc}")
                if wc * hc > cell_area * 0.6:
                    continue
                if wc * hc < 20:
                    continue
                if wc < cell.shape[1] * 0.1:
                    continue
                if hc < cell.shape[0] * 0.1:
                    continue
                parts.append((x, y, wc, hc))

            if not parts:
                # print(f"no parts for ri: {ri}, ci: {ci}")
                continue

            color = detect_color_simple(cell)
            assert color is not None, f"color is None for ri: {ri}, ci: {ci}"
            colors.append(color)
            cell_ri_ci.append((ri, ci))
            digit = classify_digit(cell, visualize=True)
            digit_ri_ci.append((ri, ci, digit))
            print(f"digit: {digit}")
            # show_wait_destroy("cell", cell)

    min_ri = min(ri for ri, _ in cell_ri_ci)
    max_ri = max(ri for ri, _ in cell_ri_ci)
    min_ci = min(ci for _, ci in cell_ri_ci)
    max_ci = max(ci for _, ci in cell_ri_ci)
    num_r = max_ri - min_ri + 1
    num_c = max_ci - min_ci + 1

    # print(f"colors: {colors}")
    print(len(colors))
    # print(colors)
    l, k = cluster_triplets(colors, show_plot=False)
    random_colors = [tuple(int(x*8)+128 for x in np.random.randint(0, 128//8, 3)) for _ in range(k)]
    board = np.full((num_r, num_c), '', dtype=object)
    for i, (ri, ci) in enumerate(cell_ri_ci):
        label = l[i]
        digit = digit_ri_ci[i][2]
        board[ri-min_ri, ci-min_ci] = f"{label}_{digit}"
    #     y1, y2 = y_lines[ri], y_lines[ri + 1]
    #     x1, x2 = x_lines[ci], x_lines[ci + 1]
    #     circle_x = (x1 + x2) // 2
    #     circle_y = (y1 + y2) // 2
    #     circle_radius = min(x2 - x1, y2 - y1) // 2
    #     cv2.circle(image_bgr, (circle_x, circle_y), circle_radius, random_colors[label], 30)
    # for i, (ri, ci) in enumerate(cell_ri_ci):
    #     digit = digit_ri_ci[i][2]
    #     y1, y2 = y_lines[ri], y_lines[ri + 1]
    #     x1, x2 = x_lines[ci], x_lines[ci + 1]
    #     circle_x = (x1 + x2) // 2
    #     circle_y = (y1 + y2) // 2
    #     cv2.putText(image_bgr, str(digit), (circle_x-5, circle_y+5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (250, 0, 0), 2)
    # show_wait_destroy("image", image_bgr)
    print(board.shape)
    print('[')
    for row in board:
        row = [f"'{c}'" + ' ' * (4 - len(c)) for c in row]
        print("        [ " + ", ".join(row) + " ],")
    print('    ]')
    return board

def pdf_to_cv_img(pdf_path, dpi=200, page=0):
    """
    Convert a PDF page to a CV2 BGR image using a given dpi (default 200).
    Uses pdf2image to do the conversion. Assumes pdf2image and pillow are installed.
    Returns a numpy (H, W, 3) dtype=uint8 BGR (cv2) image.
    """
    from pdf2image import convert_from_path

    # Convert PDF to PIL Images, pick specified page
    pil_images = convert_from_path(str(pdf_path), dpi=dpi, first_page=page+1, last_page=page+1)
    if not pil_images:
        raise RuntimeError(f"No pages rendered from {pdf_path}")

    pil_img = pil_images[0]
    # Convert PIL RGB image to numpy array, then to BGR for OpenCV
    img = np.array(pil_img)
    if img.ndim == 2:  # grayscale, expand to 3 channels
        img = np.stack([img]*3, axis=-1)
    elif img.shape[2] == 4:
        img = img[:,:,:3]
    # PIL is RGB; OpenCV expects BGR
    img = img[:, :, ::-1].copy()
    return img

def mark_white_runs(inp_path, out_path):
    img = Image.open(inp_path).convert("RGB")
    img_to_edit = Image.open(inp_path).convert("RGB")
    px = img.load()
    px_to_edit = img_to_edit.load()
    w, h = img.size
    # vertical
    x = 0
    while x < w:
        if all(px[x, y] == (255, 255, 255) for y in range(h)):
            start = x
            x += 1
            while x < w and all(px[x, y] == (255, 255, 255) for y in range(h)):
                x += 1
            mid = (start + x - 1) // 2
            for y in range(h): px_to_edit[mid, y] = (0, 0, 0)
        else:
            x += 1
    # horizontal
    y = 0
    while y < h:
        if all(px[x, y] == (255, 255, 255) for x in range(w)):
            start = y
            y += 1
            while y < h and all(px[x, y] == (255, 255, 255) for x in range(w)):
                y += 1
            mid = (start + y - 1) // 2
            for x in range(w): px_to_edit[x, mid] = (0, 0, 0)
        else:
            y += 1
    img_to_edit.save(out_path)


if __name__ == "__main__":
    # python .\src\puzzle_solver\utils\etc\parser\board_color_digit.py | python .\src\puzzle_solver\utils\visualizer.py --read_stdin
    # board = parse_board(Path(__file__).parent / 'board.png')
    # board = parse_board(Path(__file__).parent / 'Screenshot 2025-11-04 025046.png')
    # board = parse_board(Path(__file__).parent / 'Screenshot 2025-11-04 030025.png')
    inp = Path(__file__).parent / 'Screenshot 2025-11-05 at 18-41-57 Special Monthly Dominosa.png'
    outp = inp.with_suffix('.marked.png')
    mark_white_runs(inp, outp)
    board = parse_board(outp)
