from .recognizer import SimpleFaceRecognizer
from .remove_faces import remove_face_database

__all__ = [
    "SimpleFaceRecognizer",
    "remove_face_database",
    "add_person",
    "recognize_image"
]


def add_person(name, image_path):
    """
    Convenience wrapper to add a person to the face database
    without manually creating a recognizer instance.
    """
    recognizer = SimpleFaceRecognizer()
    recognizer.add_person(name, image_path)
    print(f"[INFO] Added '{name}' successfully to the known faces database")


def recognize_image(image_path, threshold=None, save_output=False):
    """
    Convenience wrapper for quick recognition using the saved database.
    Returns recognition results.
    """
    recognizer = SimpleFaceRecognizer()
    results = recognizer.recognize_image(
        input_image=image_path,
        threshold=threshold,
        save_output=save_output
    )

    # Print summary for quick feedback
    if not results:
        print("[WARN] No faces detected.")
    else:
        for r in results:
            print(f"[RESULT] {r['name']} (score={r['score']:.2f})")
    return results
