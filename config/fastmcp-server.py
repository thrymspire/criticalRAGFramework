"""
FastMCP Protocol Bridge Daemon for criticalpath-store-v1.0
Exposes indexed similarity search and metadata retrieval over port 8000.
"""
import http.server
import socketserver
import json
import psycopg2

PORT = 8000
DB_URI = "postgresql://rag_user:rag_password@127.0.0.1:5432/critical_rag"

class MCPHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "healthy", "service": "criticalpath-store-mcp"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/mcp/query":
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length).decode('utf-8'))
            query_vector = body.get("vector")
            top_k = body.get("top_k", 5)
            
            try:
                conn = psycopg2.connect(DB_URI)
                cur = conn.cursor()
                if query_vector:
                    cur.execute("""
                        SELECT chunk_id, document_id, content, metadata, 1 - (embedding <=> %s::vector) AS similarity
                        FROM rag_chunks
                        ORDER BY embedding <=> %s::vector
                        LIMIT %s;
                    """, (str(query_vector), str(query_vector), top_k))
                    rows = cur.fetchall()
                    results = [{"chunk_id": r[0], "doc_id": r[1], "content": r[2], "metadata": r[3], "score": float(r[4])} for r in rows]
                else:
                    results = []
                cur.close()
                conn.close()
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"results": results}).encode())
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    print(f"Starting FastMCP Bridge on 127.0.0.1:{PORT}...")
    with socketserver.TCPServer(("127.0.0.1", PORT), MCPHandler) as httpd:
        httpd.serve_forever()
