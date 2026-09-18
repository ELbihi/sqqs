// --- Wardrobe slots (02 Wardrobe & Pieces) --------------------------------
export const WARDROBE_SLOTS = [
  { key: "top", title: "Coat / Top", sub: "Slot 1", icon: "add", required: true },
  { key: "bottom", title: "Trouser / Skirt", sub: "Slot 2", icon: "add", required: true },
  { key: "shoes", title: "Shoes / Boots", sub: "Slot 3", icon: "add", required: true },
  { key: "bag", title: "Bag / Clutch", sub: "Optional", icon: "checkroom", required: false },
  { key: "jewelry", title: "Jewelry", sub: "Optional", icon: "diamond", required: false },
  { key: "accessory", title: "Accessory", sub: "Optional", icon: "more_horiz", required: false },
];

// --- Editorial scene presets (03 Atmosphere & Scene) ----------------------
export const SCENE_PRESETS = [
  { name: "Travertine Loft", prompt: "Sunlit brutalism, travertine walls, soft daylight" },
  { name: "Studio Minimal", prompt: "Cyclorama diffuse, seamless off-white studio backdrop" },
  { name: "Paris Haussmann", prompt: "Herringbone parquet, grand Haussmann apartment, tall windows" },
  { name: "Golden Hour Patio", prompt: "Golden hour patio, warm rim light, long shadows" },
  { name: "Moroccan Riad", prompt: "Moroccan riad courtyard, zellige tiles, dappled light" },
];

// --- 04 Look & Framing ----------------------------------------------------
// value = what the backend expects for `framing`
export const FRAMING_ANGLES = [
  { value: "full_body", label: "Full Length" },
  { value: "waist_up", label: "Three-Quarter" },
  { value: "close_up", label: "Garment Macro" },
  { value: "wide", label: "Wide Environment" },
];

// Output format / aspect ratio
export const FORMATS = [
  { value: "4:5", label: "Editorial", hint: "4:5 portrait" },
  { value: "9:16", label: "Story", hint: "9:16 vertical" },
  { value: "1:1", label: "Square", hint: "1:1 post" },
  { value: "16:9", label: "Landscape", hint: "16:9 wide" },
];

// Movement / motion presets
export const POSES = [
  "Standing",
  "Walk forward",
  "Walk backward",
  "Turn left",
  "Turn right",
  "Turn around",
  "360-degree product view",
  "Wave",
  "Cross arms",
  "Look left/right",
  "Sit",
];

// Editorial / fashion poses
export const FASHION_POSES = [
  "Fashion pose",
  "Runway walk",
  "One hand resting on hip",
  "Both hands on hips",
  "Arms raised overhead",
  "Hands in pockets",
  "Arms crossed casually",
  "Leaning against a wall",
  "Over-the-shoulder glance",
  "Looking down, contemplative",
  "Walking toward camera",
  "Half-turn showing the back",
  "Hand touching hair",
  "Adjusting the collar",
  "Seated on a stool",
  "Legs crossed, standing",
  "Candid looking away",
  "Power stance",
  "Static mannequin",
  "Fluid movement",
];

export const POSE_ATTITUDES = FASHION_POSES;
