import cv2
import json

# === CONFIG ===
video_path = "ML Model/video test/testvid2.mp4" 
output_json = "predefined_spots.json"
frame_save_path = "first_frame.jpg"

# === Extract First Frame ===
cap = cv2.VideoCapture(video_path)
ret, frame = cap.read()
cap.release()

if not ret:
    print("❌ Error reading video.")
    exit()

cv2.imwrite(frame_save_path, frame)
print(f"✅ Saved first frame to {frame_save_path}")

# === Globals for Spot Drawing ===
clicked_points = []
predefined_spots = {}
spot_counter = 1

# === Mouse Callback ===
def click_event(event, x, y, flags, param):
    global clicked_points, spot_counter

    if event == cv2.EVENT_LBUTTONDOWN:
        clicked_points.append((x, y))
        print(f"🖱️ Clicked: ({x}, {y})")

        if len(clicked_points) % 2 == 0:
            pt1 = clicked_points[-2]
            pt2 = clicked_points[-1]
            spot_id = f"spot_{spot_counter}"
            predefined_spots[spot_id] = [pt1[0], pt1[1], pt2[0], pt2[1]]
            print(f"✅ {spot_id}: {predefined_spots[spot_id]}")
            spot_counter += 1

            redraw_boxes()

# === Redraw All Boxes ===
def redraw_boxes():
    temp = frame.copy()
    for sid, (x1, y1, x2, y2) in predefined_spots.items():
        cv2.rectangle(temp, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.putText(temp, sid, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
    cv2.imshow("Define Parking Spots", temp)

# === Setup GUI ===
cv2.imshow("Define Parking Spots", frame)
cv2.setMouseCallback("Define Parking Spots", click_event)
print("\n🖱️ Click TOP-LEFT then BOTTOM-RIGHT of each spot.")
print("💾 Press ESC when done to save coordinates.\n")

while True:
    key = cv2.waitKey(1) & 0xFF
    if key == 27:  # ESC key
        break

cv2.destroyAllWindows()

# === Save Spot Definitions ===
with open(output_json, "w") as f:
    json.dump(predefined_spots, f, indent=4)

print(f"\n✅ Saved {len(predefined_spots)} spots to {output_json}")