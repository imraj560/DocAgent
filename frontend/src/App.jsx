import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8000";

function App() {
  const [files, setFiles] = useState([]);
  const [sessionId, setSessionId] = useState(null);
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [verification, setVerification] = useState("");
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (event) => {
    setFiles(Array.from(event.target.files));
    setError("");
  };

  const uploadDocuments = async () => {
    if (files.length === 0) {
      setError("Please select at least one document.");
      return;
    }

    setUploading(true);
    setError("");
    setAnswer("");
    setVerification("");

    const formData = new FormData();

    files.forEach((file) => {
      formData.append("files", file);
    });

    try {
      const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Upload failed.");
      }

      setSessionId(data.session_id);

      console.log("Upload successful:", data);
    } catch (err) {
      setError(err.message);
      setSessionId(null);
    } finally {
      setUploading(false);
    }
  };

  const askQuestion = async (event) => {
    event.preventDefault();

    if (!sessionId) {
      setError("Please upload your documents first.");
      return;
    }

    if (!question.trim()) {
      setError("Please enter a question.");
      return;
    }

    setLoading(true);
    setError("");
    setAnswer("");
    setVerification("");

    try {
      const response = await fetch(`${API_URL}/ask`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          session_id: sessionId,
          question: question,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || "Failed to process question.");
      }

      setAnswer(data.answer);
      setVerification(data.verification);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="app">
      <div className="container">

        <header>
          <h1>DocChat</h1>
          <p>
            Upload your documents and ask questions about their contents.
          </p>
        </header>

        {/* Upload Section */}
        <section className="card">
          <h2>1. Upload Documents</h2>

          <input
            type="file"
            multiple
            onChange={handleFileChange}
          />

          {files.length > 0 && (
            <div className="file-list">
              <h3>Selected files</h3>

              {files.map((file, index) => (
                <div className="file" key={index}>
                  📄 {file.name}
                </div>
              ))}
            </div>
          )}

          <button
            onClick={uploadDocuments}
            disabled={uploading || files.length === 0}
          >
            {uploading ? "Processing..." : "Upload Documents"}
          </button>

          {sessionId && (
            <div className="success">
              Documents uploaded successfully.
              <br />
              <small>Session: {sessionId}</small>
            </div>
          )}
        </section>

        {/* Question Section */}
        <section className="card">
          <h2>2. Ask a Question</h2>

          <form onSubmit={askQuestion}>
            <textarea
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Example: What skills are mentioned in my resume?"
              rows={4}
              disabled={!sessionId || loading}
            />

            <button
              type="submit"
              disabled={!sessionId || loading}
            >
              {loading ? "Thinking..." : "Ask Question"}
            </button>
          </form>
        </section>

        {/* Error */}
        {error && (
          <div className="error">
            {error}
          </div>
        )}

        {/* Answer */}
        {answer && (
          <section className="card">
            <h2>Answer</h2>

            <div className="answer">
              {answer}
            </div>
          </section>
        )}

        {/* Verification */}
        {verification && (
          <section className="card verification">
            <h2>Verification</h2>

            <pre>{verification}</pre>
          </section>
        )}

      </div>
    </div>
  );
}

export default App;