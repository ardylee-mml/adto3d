import { useState } from "react";
import axios from "axios";
import styles from "../styles/Upload.module.css";
import ModelViewer from "../components/ModelViewer";

export default function Upload() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string>("");
  const [modelUrl, setModelUrl] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setPreview(URL.createObjectURL(e.target.files[0]));
      setModelUrl("");
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setLoading(true);
    setError("");

    const formData = new FormData();
    formData.append("image", file);

    try {
      const response = await axios.post("/api/convert", formData);
      setModelUrl(response.data.downloadUrl);
    } catch (err) {
      setError("Error converting image");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <form onSubmit={handleSubmit} className={styles.form}>
        <input
          type="file"
          accept="image/*"
          onChange={handleFileChange}
          className={styles.input}
        />
        {preview && (
          <img src={preview} alt="Preview" className={styles.preview} />
        )}
        <button type="submit" disabled={!file || loading}>
          {loading ? "Converting..." : "Convert to 3D"}
        </button>
        {error && <p className={styles.error}>{error}</p>}
      </form>

      {modelUrl && (
        <div className={styles.result}>
          <h3>3D Model Preview</h3>
          <ModelViewer modelUrl={modelUrl} />
          <a href={modelUrl} download className={styles.download}>
            Download 3D Model
          </a>
        </div>
      )}
    </div>
  );
}
