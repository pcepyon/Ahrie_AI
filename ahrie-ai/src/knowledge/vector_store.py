"""LanceDB vector store for semantic search and knowledge retrieval."""

import lancedb
import pyarrow as pa
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from openai import AsyncOpenAI
import logging
from datetime import datetime
import json

from src.utils.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for managing embeddings and semantic search using LanceDB.
    """
    
    def __init__(self, db_path: str = "./data/lancedb"):
        """
        Initialize the vector store.
        
        Args:
            db_path: Path to LanceDB database
        """
        self.db_path = db_path
        self.db = lancedb.connect(db_path)
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.embedding_model = "text-embedding-3-small"
        self.embedding_dimension = 1536
        
        # Initialize tables
        self._init_tables()
    
    def _init_tables(self) -> None:
        """Initialize required tables in the vector store."""
        # Medical procedures table
        if "procedures" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("name", pa.string()),
                pa.field("name_ar", pa.string()),
                pa.field("name_ko", pa.string()),
                pa.field("category", pa.string()),
                pa.field("description", pa.string()),
                pa.field("content", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), self.embedding_dimension)),
                pa.field("metadata", pa.string()),
                pa.field("created_at", pa.string())
            ])
            self.db.create_table("procedures", schema=schema)
            logger.info("Created procedures table")
        
        # Clinics table
        if "clinics" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("name", pa.string()),
                pa.field("description", pa.string()),
                pa.field("specialties", pa.string()),
                pa.field("content", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), self.embedding_dimension)),
                pa.field("metadata", pa.string()),
                pa.field("created_at", pa.string())
            ])
            self.db.create_table("clinics", schema=schema)
            logger.info("Created clinics table")
        
        # Reviews table
        if "reviews" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("video_id", pa.string()),
                pa.field("title", pa.string()),
                pa.field("content", pa.string()),
                pa.field("language", pa.string()),
                pa.field("sentiment", pa.float32()),
                pa.field("embedding", pa.list_(pa.float32(), self.embedding_dimension)),
                pa.field("metadata", pa.string()),
                pa.field("created_at", pa.string())
            ])
            self.db.create_table("reviews", schema=schema)
            logger.info("Created reviews table")
        
        # FAQ table
        if "faqs" not in self.db.table_names():
            schema = pa.schema([
                pa.field("id", pa.string()),
                pa.field("question", pa.string()),
                pa.field("answer", pa.string()),
                pa.field("category", pa.string()),
                pa.field("language", pa.string()),
                pa.field("embedding", pa.list_(pa.float32(), self.embedding_dimension)),
                pa.field("metadata", pa.string()),
                pa.field("created_at", pa.string())
            ])
            self.db.create_table("faqs", schema=schema)
            logger.info("Created FAQs table")
    
    async def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for given text using OpenAI.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector
        """
        try:
            response = await self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
            
        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            # Return zero vector on error
            return [0.0] * self.embedding_dimension
    
    async def add_procedure(self, procedure_data: Dict[str, Any]) -> str:
        """
        Add a medical procedure to the vector store.
        
        Args:
            procedure_data: Procedure information
            
        Returns:
            Procedure ID
        """
        try:
            # Prepare content for embedding
            content = f"""
            Procedure: {procedure_data.get('name', '')}
            Category: {procedure_data.get('category', '')}
            Description: {procedure_data.get('description', '')}
            Duration: {procedure_data.get('duration', '')}
            Recovery: {procedure_data.get('recovery_time', '')}
            Benefits: {', '.join(procedure_data.get('benefits', []))}
            Risks: {', '.join(procedure_data.get('risks', []))}
            """
            
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Create record
            procedure_id = f"proc_{datetime.now().timestamp()}"
            record = {
                "id": procedure_id,
                "name": procedure_data.get('name', ''),
                "name_ar": procedure_data.get('name_ar', ''),
                "name_ko": procedure_data.get('name_ko', ''),
                "category": procedure_data.get('category', ''),
                "description": procedure_data.get('description', ''),
                "content": content,
                "embedding": embedding,
                "metadata": json.dumps(procedure_data),
                "created_at": datetime.now().isoformat()
            }
            
            # Add to table
            table = self.db.open_table("procedures")
            table.add([record])
            
            logger.info(f"Added procedure: {procedure_data.get('name')}")
            return procedure_id
            
        except Exception as e:
            logger.error(f"Error adding procedure: {str(e)}")
            raise
    
    async def add_clinic(self, clinic_data: Dict[str, Any]) -> str:
        """
        Add a clinic to the vector store.
        
        Args:
            clinic_data: Clinic information
            
        Returns:
            Clinic ID
        """
        try:
            # Prepare content for embedding
            specialties = ', '.join(clinic_data.get('specialties', []))
            languages = ', '.join(clinic_data.get('languages_supported', []))
            
            content = f"""
            Clinic: {clinic_data.get('name', '')}
            Location: {clinic_data.get('address', '')}
            Specialties: {specialties}
            Languages: {languages}
            Description: {clinic_data.get('description', '')}
            Halal Friendly: {clinic_data.get('halal_friendly', False)}
            Arabic Support: {clinic_data.get('arabic_support', False)}
            """
            
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Create record
            clinic_id = f"clinic_{datetime.now().timestamp()}"
            record = {
                "id": clinic_id,
                "name": clinic_data.get('name', ''),
                "description": clinic_data.get('description', ''),
                "specialties": specialties,
                "content": content,
                "embedding": embedding,
                "metadata": json.dumps(clinic_data),
                "created_at": datetime.now().isoformat()
            }
            
            # Add to table
            table = self.db.open_table("clinics")
            table.add([record])
            
            logger.info(f"Added clinic: {clinic_data.get('name')}")
            return clinic_id
            
        except Exception as e:
            logger.error(f"Error adding clinic: {str(e)}")
            raise
    
    async def add_review(self, review_data: Dict[str, Any]) -> str:
        """
        Add a review to the vector store.
        
        Args:
            review_data: Review information
            
        Returns:
            Review ID
        """
        try:
            # Prepare content for embedding
            content = f"""
            Title: {review_data.get('title', '')}
            Review: {review_data.get('content', '')}
            Procedure: {review_data.get('procedure', '')}
            Clinic: {review_data.get('clinic', '')}
            Rating: {review_data.get('rating', '')}
            """
            
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Create record
            review_id = f"review_{datetime.now().timestamp()}"
            record = {
                "id": review_id,
                "video_id": review_data.get('video_id', ''),
                "title": review_data.get('title', ''),
                "content": content,
                "language": review_data.get('language', 'en'),
                "sentiment": float(review_data.get('sentiment', 0.0)),
                "embedding": embedding,
                "metadata": json.dumps(review_data),
                "created_at": datetime.now().isoformat()
            }
            
            # Add to table
            table = self.db.open_table("reviews")
            table.add([record])
            
            logger.info(f"Added review: {review_data.get('title')}")
            return review_id
            
        except Exception as e:
            logger.error(f"Error adding review: {str(e)}")
            raise
    
    async def add_faq(self, faq_data: Dict[str, Any]) -> str:
        """
        Add an FAQ to the vector store.
        
        Args:
            faq_data: FAQ information
            
        Returns:
            FAQ ID
        """
        try:
            # Prepare content for embedding
            content = f"Question: {faq_data.get('question', '')} Answer: {faq_data.get('answer', '')}"
            
            # Generate embedding
            embedding = await self.generate_embedding(content)
            
            # Create record
            faq_id = f"faq_{datetime.now().timestamp()}"
            record = {
                "id": faq_id,
                "question": faq_data.get('question', ''),
                "answer": faq_data.get('answer', ''),
                "category": faq_data.get('category', ''),
                "language": faq_data.get('language', 'en'),
                "embedding": embedding,
                "metadata": json.dumps(faq_data),
                "created_at": datetime.now().isoformat()
            }
            
            # Add to table
            table = self.db.open_table("faqs")
            table.add([record])
            
            logger.info(f"Added FAQ: {faq_data.get('question')}")
            return faq_id
            
        except Exception as e:
            logger.error(f"Error adding FAQ: {str(e)}")
            raise
    
    async def search(self, 
                    query: str,
                    table_name: str,
                    limit: int = 5,
                    filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Perform semantic search in a specific table.
        
        Args:
            query: Search query
            table_name: Table to search in
            limit: Maximum number of results
            filters: Optional filters to apply
            
        Returns:
            List of search results
        """
        try:
            # Generate query embedding
            query_embedding = await self.generate_embedding(query)
            
            # Open table
            table = self.db.open_table(table_name)
            
            # Perform vector search
            results = table.search(query_embedding).limit(limit)
            
            # Apply filters if provided
            if filters:
                for key, value in filters.items():
                    results = results.where(f"{key} = '{value}'")
            
            # Execute search
            search_results = results.to_list()
            
            # Parse results
            parsed_results = []
            for result in search_results:
                parsed_result = {
                    "id": result.get("id"),
                    "score": result.get("_distance", 0),
                    "content": result.get("content", ""),
                    "metadata": json.loads(result.get("metadata", "{}"))
                }
                
                # Add table-specific fields
                if table_name == "procedures":
                    parsed_result["name"] = result.get("name")
                    parsed_result["category"] = result.get("category")
                elif table_name == "clinics":
                    parsed_result["name"] = result.get("name")
                    parsed_result["specialties"] = result.get("specialties")
                elif table_name == "reviews":
                    parsed_result["title"] = result.get("title")
                    parsed_result["sentiment"] = result.get("sentiment")
                elif table_name == "faqs":
                    parsed_result["question"] = result.get("question")
                    parsed_result["answer"] = result.get("answer")
                
                parsed_results.append(parsed_result)
            
            return parsed_results
            
        except Exception as e:
            logger.error(f"Error searching {table_name}: {str(e)}")
            return []
    
    async def hybrid_search(self,
                          query: str,
                          limit: int = 5) -> Dict[str, List[Dict[str, Any]]]:
        """
        Perform search across all tables.
        
        Args:
            query: Search query
            limit: Maximum results per table
            
        Returns:
            Dictionary with results from each table
        """
        results = {}
        
        # Search all tables
        for table_name in ["procedures", "clinics", "reviews", "faqs"]:
            table_results = await self.search(query, table_name, limit)
            if table_results:
                results[table_name] = table_results
        
        return results
    
    async def update_embeddings(self, table_name: str) -> int:
        """
        Update embeddings for all records in a table.
        
        Args:
            table_name: Table to update
            
        Returns:
            Number of records updated
        """
        try:
            table = self.db.open_table(table_name)
            records = table.to_pandas()
            updated_count = 0
            
            for index, row in records.iterrows():
                # Generate new embedding
                content = row.get("content", "")
                if content:
                    new_embedding = await self.generate_embedding(content)
                    
                    # Update record
                    table.update(
                        where=f"id = '{row['id']}'",
                        values={"embedding": new_embedding}
                    )
                    updated_count += 1
            
            logger.info(f"Updated {updated_count} embeddings in {table_name}")
            return updated_count
            
        except Exception as e:
            logger.error(f"Error updating embeddings: {str(e)}")
            return 0
    
    def get_table_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector store tables.
        
        Returns:
            Dictionary with table statistics
        """
        stats = {}
        
        for table_name in self.db.table_names():
            table = self.db.open_table(table_name)
            stats[table_name] = {
                "count": len(table),
                "columns": table.schema.names
            }
        
        return stats