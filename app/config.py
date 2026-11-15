SUPPORTED_EXTENSIONS = {".txt", ".pdf", ".docx"}
MODEL_NAME = "all-MiniLM-L6-v2"

# Canonical skill mappings: Canonical Skill Name -> List of aliases and representations
SKILL_ALIASES = {
    "python": ["python", "python3", "py"],
    "sql": ["sql", "mysql", "postgresql", "postgres", "sqlite", "tsql", "plsql"],
    "nosql": ["nosql", "mongodb", "cassandra", "dynamodb", "couchbase"],
    "fastapi": ["fastapi"],
    "flask": ["flask"],
    "django": ["django"],
    "machine learning": ["machine learning", "ml"],
    "deep learning": ["deep learning", "dl"],
    "natural language processing": ["natural language processing", "nlp"],
    "computer vision": ["computer vision", "cv"],
    "large language models": ["large language models", "large language model", "llm", "llms"],
    "retrieval-augmented generation": ["retrieval-augmented generation", "retrieval augmented generation", "rag"],
    "langchain": ["langchain"],
    "llamaindex": ["llamaindex", "llama-index"],
    "transformers": ["transformers", "hugging face", "huggingface"],
    "sentence-transformers": ["sentence-transformers", "sentence transformers", "sentence-transformer"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    "scikit-learn": ["scikit-learn", "sklearn"],
    "pandas": ["pandas"],
    "numpy": ["numpy"],
    "scipy": ["scipy"],
    "data analysis": ["data analysis", "data analytics", "exploratory data analysis", "eda"],
    "statistics": ["statistics", "statistical analysis", "statistical modeling"],
    "vector database": ["vector database", "vector db", "faiss", "chromadb", "chroma", "pinecone", "weaviate", "qdrant", "milvus"],
    "docker": ["docker", "containerization", "containers"],
    "kubernetes": ["kubernetes", "k8s"],
    "git": ["git", "github", "gitlab"],
    "ci/cd": ["ci/cd", "cicd", "continuous integration", "continuous deployment"],
    "aws": ["aws", "amazon web services", "ec2", "s3", "lambda"],
    "azure": ["azure", "microsoft azure"],
    "gcp": ["gcp", "google cloud", "google cloud platform"],
    "linux": ["linux", "bash", "shell scripting", "unix"],
    "rest api": ["rest api", "rest apis", "restful", "restful api", "restful apis"],
    "graphql": ["graphql"],
    "microservices": ["microservices", "microservice architecture"],
    "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"],
    "react": ["react", "react.js", "reactjs"],
    "node.js": ["node.js", "nodejs", "node"],
    "c++": ["c++", "cpp"],
    "java": ["java"],
}

# Flat vocabulary set of all canonical skills
SKILL_VOCABULARY = set(SKILL_ALIASES.keys())

