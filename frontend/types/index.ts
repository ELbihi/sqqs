export interface User {
  id: string;
  email: string;
  full_name?: string | null;
  credits: number;
}

export interface Character {
  id: string;
  name: string;
  source: string;
  original_photo_key?: string | null;
  photos?: { storage_key: string; label: string }[];
}

export interface Garment {
  id: string;
  name: string;
  category?: string | null;
  brand?: string | null;
  original_image_key?: string | null;
}

export interface Background {
  id: string;
  name: string;
  source: string;
  image_key?: string | null;
  prompt?: string | null;
}

export interface GenerationAsset {
  id: string;
  kind: "image" | "video" | "thumbnail";
  storage_key: string;
}

export type GenerationStatus =
  | "QUEUED"
  | "PROCESSING"
  | "PREPARING_CHARACTER"
  | "PREPARING_GARMENT"
  | "GENERATING"
  | "GENERATING_VIDEO"
  | "UPSCALING"
  | "COMPLETED"
  | "FAILED";

export interface Generation {
  id: string;
  output_type: "image" | "video";
  status: GenerationStatus;
  error?: string | null;
  credits_cost: number;
  pose?: string | null;
  instruction?: string | null;
  assets: GenerationAsset[];
}
