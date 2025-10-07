declare module 'react-leaflet-heatmap-layer-v3' {
  import { ComponentType } from 'react';

  interface HeatmapLayerProps {
    points: Array<any>;
    longitudeExtractor: (point: any) => number;
    latitudeExtractor: (point: any) => number;
    intensityExtractor: (point: any) => number;
    max?: number;
    radius?: number;
    blur?: number;
    gradient?: { [key: number]: string };
    minOpacity?: number;
  }

  export const HeatmapLayer: ComponentType<HeatmapLayerProps>;
  export default HeatmapLayer;
}
