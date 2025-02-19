export interface LogoTexture {
    id: string;
    texture: THREE.Texture;
    scale: { x: number; y: number };
    position: { x: number; y: number };
    rotation: number;
    opacity: number;
    blendMode: 'normal' | 'multiply' | 'add' | 'subtract';
}

export interface UVSettings {
    tiling: { x: number; y: number };
    offset: { x: number; y: number };
} 