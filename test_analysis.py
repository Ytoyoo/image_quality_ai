from services.analysis import analyze_sharpness, analyze_motion_blur

path = "static/uploads/original/sharpen_2444b807c8e54a9b8de17d41da31aeaa_Screenshot_from_2025-07-19_20-40-50.png"

sharpness = analyze_sharpness(path)
motion_blur = analyze_motion_blur(path)

print("Sharpness:", sharpness)
print("Motion blur score:", motion_blur)
