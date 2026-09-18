"""Shared camera framing instructions for image and video providers."""
FRAMING = {
    "close_up": "Close-up portrait: frame the head and shoulders, with comfortable space above the head. The face is prominent; lower clothing may be outside the frame.",
    "waist_up": "Medium shot: frame the person from the waist upward, with headroom and both shoulders visible. Do not crop the face.",
    "full_body": "Full-body shot from a comfortable distance: show the entire person from head to shoes, with clear space above the head and below the feet. The person occupies about 70 percent of the image height.",
    "wide": "Wide environmental shot: move the camera farther away. Show the entire person head to toe at about 45 percent of image height, with generous visible surroundings on all sides.",
}

def framing_prompt(recipe):
    choice = (recipe.get("params") or {}).get("framing", "full_body")
    return "CAMERA FRAMING: " + FRAMING.get(choice, FRAMING["full_body"]) + " Use the reference photos for identity, not their crop or camera distance. This selected framing takes priority over conflicting crop instructions."
