from services.image_analysis import analyze_image
from services.decision_engine import decide_processing_actions
from services.image_processing import process_image

image_path = "static/uploads/original/lena.png"
output_dir = "static/results"

analysis = analyze_image(image_path)
actions = decide_processing_actions(analysis)

print("Actions:", actions)

result_filename = process_image(image_path, actions, output_dir)
print("Saved as:", result_filename)
