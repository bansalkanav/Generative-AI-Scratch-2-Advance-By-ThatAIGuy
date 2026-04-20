import redis
import pickle
from datetime import datetime, timedelta

class HybridStore:
    """Redis primary, PostgreSQL fallback"""
    
    def __init__(self, redis_client, postgres_store, redis_ttl=3600):
        self.redis = redis_client
        self.postgres = postgres_store
        self.redis_ttl = redis_ttl  # 1 hour in Redis
    
    def mget(self, keys):
        """Get from Redis, fallback to PostgreSQL"""
        results = [None] * len(keys)
        missing_indices = []
        
        # Try Redis first
        for i, key in enumerate(keys):
            val = self.redis.get(key)
            if val:
                results[i] = pickle.loads(val)
            else:
                missing_indices.append(i)
        
        # Fallback to PostgreSQL for missing keys
        if missing_indices:
            missing_keys = [keys[i] for i in missing_indices]
            pg_results = self.postgres.mget(missing_keys)
            
            for idx, pg_idx in enumerate(missing_indices):
                if pg_results[idx]:
                    results[pg_idx] = pg_results[idx]
                    # Cache in Redis for next time
                    self.redis.setex(
                        missing_keys[idx],
                        self.redis_ttl,
                        pickle.dumps(pg_results[idx])
                    )
        
        return results
    
    def mset(self, key_value_pairs):
        """Write to both Redis and PostgreSQL"""
        # Fast Redis write
        for key, value in key_value_pairs:
            self.redis.setex(
                key,
                self.redis_ttl,
                pickle.dumps(value)
            )
        
        # Persistent PostgreSQL write
        self.postgres.mset(key_value_pairs)

# Usage
redis_client = redis.Redis(host="localhost", port=6379)
postgres_store = PostgresStore("postgresql://...")
hybrid_store = HybridStore(redis_client, postgres_store)

embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
cached_embeddings = CacheBackedEmbeddings.from_bytes_store(
    underlying_embeddings=embeddings,
    document_embedding_cache=hybrid_store,
    namespace="hybrid-cache"
)