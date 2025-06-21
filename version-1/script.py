import cv2
import os
import pandas as pd

IMG_DIR = "./train"
SAVE_CSV = "grouth_truth.csv"

data = []
if os.path.exists(SAVE_CSV):
    data = pd.read_csv(SAVE_CSV).values.tolist()
    done = {row[0] for row in data}
else:
    done = set()

def draw_text(img, text):
    display = img.copy()
    cv2.rectangle(display, (10, img.shape[0]-40), (600, img.shape[0]-10), (0,0,0), -1)
    cv2.putText(display, f"Enter plate: {text}", (20, img.shape[0]-15),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)
    return display

for fname in sorted(os.listdir(IMG_DIR)):
    if not fname.lower().endswith((".jpg", ".png", ".jpeg")) or fname in done:
        continue

    img_path = os.path.join(IMG_DIR, fname)
    img = cv2.imread(img_path)
    if img is None:
        continue

    h, w = img.shape[:2]
    scale = 900 / max(h, w)
    img_resized = cv2.resize(img, (int(w * scale), int(h * scale)))
    
    plate_text = ""
    while True:
        disp = draw_text(img_resized, plate_text)
        cv2.imshow("Label Plate", disp)
        key = cv2.waitKey(0)

        if key == 13:  # Enter key
            break
        elif key == 8:  # Backspace
            plate_text = plate_text[:-1]
        elif key == 27:  # Esc to skip
            plate_text = ""
            break
        elif key in range(32, 127):  # Valid ASCII char
            plate_text += chr(key)

    cv2.destroyAllWindows()

    if plate_text.strip() == "":
        continue  # skipped

    data.append([fname, plate_text])
    pd.DataFrame(data, columns=["filename", "plate_text"]).to_csv(SAVE_CSV, index=False)
