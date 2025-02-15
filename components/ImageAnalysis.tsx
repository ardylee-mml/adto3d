import { useState } from "react";
import styles from "../styles/ImageAnalysis.module.css";

interface AnalysisResult {
  dimensions: {
    width: number;
    height: number;
    aspect_ratio: number;
  };
  complexity: {
    edge_count: number;
    contour_count: number;
  };
  color: {
    average_rgb: number[];
  };
  shape: {
    type: string;
    circularity: number;
    symmetry: string;
  };
}

export default function ImageAnalysis({
  analysis,
}: {
  analysis: AnalysisResult;
}) {
  if (!analysis) return null;

  const rgbColor = analysis.color?.average_rgb;
  const colorStyle = rgbColor
    ? {
        backgroundColor: `rgb(${rgbColor[0]}, ${rgbColor[1]}, ${rgbColor[2]})`,
      }
    : {};

  return (
    <div className={styles.analysisContainer}>
      <h3>Image Analysis Results</h3>

      <div className={styles.section}>
        <h4>Dimensions</h4>
        <p>Width: {analysis.dimensions.width}px</p>
        <p>Height: {analysis.dimensions.height}px</p>
        <p>Aspect Ratio: {analysis.dimensions.aspect_ratio}</p>
      </div>

      <div className={styles.section}>
        <h4>Shape Analysis</h4>
        <p>Type: {analysis.shape.type}</p>
        <p>Symmetry: {analysis.shape.symmetry}</p>
        <p>Circularity: {analysis.shape.circularity}</p>
      </div>

      <div className={styles.section}>
        <h4>Complexity</h4>
        <p>Edge Count: {analysis.complexity.edge_count}</p>
        <p>Contour Count: {analysis.complexity.contour_count}</p>
      </div>

      <div className={styles.section}>
        <h4>Color</h4>
        <div className={styles.colorPreview} style={colorStyle}></div>
        <p>RGB: ({analysis.color.average_rgb.join(", ")})</p>
      </div>
    </div>
  );
}
