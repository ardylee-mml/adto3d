import { useState } from "react";
import styles from "../styles/Upload.module.css";
import ImageAnalysis from "../components/ImageAnalysis";

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

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setPreview(URL.createObjectURL(selectedFile));
      setAnalysis(null);
      setError("");
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    setLoading(true);
    setError("");

    try {
      const formData = new FormData();
      formData.append("image", file);

      const response = await fetch("/api/convert", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.error || "Upload failed");
      }

      setAnalysis(data.analysis);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Upload failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1>2D to 3D Converter</h1>

      <div className={styles.uploadSection}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className={styles.fileInput}
        />

        {preview && (
          <div className={styles.previewContainer}>
            <img src={preview} alt="Preview" className={styles.preview} />
          </div>
        )}

        <button
          onClick={handleUpload}
          disabled={!file || loading}
          className={styles.uploadButton}
        >
          {loading ? "Processing..." : "Analyze Image"}
        </button>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {analysis && <ImageAnalysis analysis={analysis} />}
    </div>
  );
}
