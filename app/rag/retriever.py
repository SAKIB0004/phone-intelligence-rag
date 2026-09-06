import re
from pathlib import Path
from typing import List

import chromadb

from app.config.settings import settings
from app.database.connection import get_db
from app.database.crud import get_all_phones
from app.database.models import PhoneSpec
from app.rag.embeddings import create_embedding_function
from app.utils.logger import logger


class SamsungRAGRetriever:

    def __init__(self):
        Path(settings.CHROMA_PERSIST_DIR).mkdir(
            parents=True,
            exist_ok=True,
        )

        self.chroma_client = chromadb.PersistentClient(
            path=settings.CHROMA_PERSIST_DIR
        )

        self.embedding_fn = create_embedding_function(settings.EMBEDDING_MODEL)

        self.collection = self.chroma_client.get_or_create_collection(
            name="samsung_phones",
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    # ---------------------------------------------------------
    # DOCUMENT CREATION
    # ---------------------------------------------------------

    def _phone_to_document(self, phone: PhoneSpec) -> str:
        """Convert a phone database record into searchable text."""

        return (
            f"Device Model: {phone.model_name}\n"
            f"Brand: {phone.brand}\n"
            f"Release Date: {phone.release_date or 'N/A'}\n"
            f"Dimensions: {phone.dimensions or 'N/A'}\n"
            f"Weight: {phone.weight_g or 'N/A'} g\n"
            f"Display Size: {phone.display_size_inches or 'N/A'} inches\n"
            f"Display Type: {phone.display_type or 'N/A'}\n"
            f"Resolution: {phone.resolution or 'N/A'}\n"
            f"Operating System: {phone.os or 'N/A'}\n"
            f"Chipset: {phone.chipset or 'N/A'}\n"
            f"CPU: {phone.cpu or 'N/A'}\n"
            f"GPU: {phone.gpu or 'N/A'}\n"
            f"Memory and Storage: {phone.storage_ram or 'N/A'}\n"
            f"Main Camera: {phone.main_camera or 'N/A'}\n"
            f"Selfie Camera: {phone.selfie_camera or 'N/A'}\n"
            f"Battery Capacity: "
            f"{phone.battery_capacity_mah or 'N/A'} mAh\n"
            f"Charging: {phone.charging_speed or 'N/A'}\n"
            f"Price: {phone.price or 'N/A'}\n"
        )

    # ---------------------------------------------------------
    # PHONE NAME NORMALIZATION
    # ---------------------------------------------------------

    @staticmethod
    def _normalize_model_name(model_name: str) -> str:
        """Normalize common Samsung phone name variations."""

        name = model_name.lower().strip()

        replacements = {
            "samsung galaxy": "galaxy",
            "samsung": "",
            "5g": "",
        }

        for old, new in replacements.items():
            name = name.replace(old, new)

        name = re.sub(r"\s+", " ", name)

        return name.strip()

    # ---------------------------------------------------------
    # FIND PHONE
    # ---------------------------------------------------------

    def _find_phone(self, db, model_name):
        """Find a phone using normalized model-name matching."""

        normalized_query = self._normalize_model_name(model_name)

        phones = get_all_phones(db)

        # First: exact normalized match
        for phone in phones:
            normalized_db_name = self._normalize_model_name(
                phone.model_name
            )

            if normalized_db_name == normalized_query:
                return phone

        # Second: partial match
        for phone in phones:
            normalized_db_name = self._normalize_model_name(
                phone.model_name
            )

            if (
                normalized_query in normalized_db_name
                or normalized_db_name in normalized_query
            ):
                return phone

        return None

    # ---------------------------------------------------------
    # INDEX DATABASE
    # ---------------------------------------------------------

    def index_database(self, force_refresh: bool = False):
        """Synchronize PostgreSQL records with ChromaDB."""

        with get_db() as db:
            phones = get_all_phones(db)

            if not phones:
                logger.warning(
                    "No phones found in PostgreSQL to index."
                )
                return 0

            records = []

            for phone in phones:
                records.append(
                    {
                        "id": f"phone_{phone.id}",
                        "document": self._phone_to_document(phone),
                        "metadata": {
                            "id": phone.id,
                            "model_name": phone.model_name,
                            "battery_capacity_mah": (
                                phone.battery_capacity_mah or 0
                            ),
                            "display_size_inches": (
                                phone.display_size_inches or 0.0
                            ),
                            "chipset": phone.chipset or "Unknown",
                        },
                    }
                )

        if force_refresh:
            try:
                self.chroma_client.delete_collection(
                    "samsung_phones"
                )
            except Exception:
                pass

            self.collection = self.chroma_client.create_collection(
                name="samsung_phones",
                embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine"},
            )

        ids = [record["id"] for record in records]
        documents = [record["document"] for record in records]
        metadatas = [record["metadata"] for record in records]

        # Upsert instead of add.
        #
        # This is important because it allows newly scraped
        # or updated PostgreSQL records to synchronize safely.
        self.collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            f"Successfully indexed {len(records)} phones "
            f"in ChromaDB."
        )

        return len(records)


    # ---------------------------------------------------------
    # COMPARISON RETRIEVAL
    # ---------------------------------------------------------

    def retrieve_comparison(
        self,
        model_names: List[str],
    ) -> str:
        """Retrieve complete specifications for multiple phones."""

        contexts = []

        with get_db() as db:
            for model_name in model_names:
                phone = self._find_phone(
                    db,
                    model_name,
                )

                if phone:
                    contexts.append(
                        self._phone_to_document(phone)
                    )
                    logger.info(
                        f"Comparison phone found: "
                        f"{phone.model_name}"
                    )
                else:
                    logger.warning(
                        f"Comparison phone not found: "
                        f"{model_name}"
                    )

        if not contexts:
            return (
                "No matching phone data found "
                "in database."
            )

        return "\n---\n".join(contexts)

    # ---------------------------------------------------------
    # BATTERY RANKING
    # ---------------------------------------------------------

    def retrieve_best_battery(
        self,
        limit: int = 5,
    ) -> str:
        """Retrieve phones with the largest battery capacities."""

        with get_db() as db:
            phones = (
                db.query(PhoneSpec)
                .filter(
                    PhoneSpec.battery_capacity_mah.isnot(None)
                )
                .order_by(
                    PhoneSpec.battery_capacity_mah.desc()
                )
                .limit(limit)
                .all()
            )

            if not phones:
                return (
                    "No battery information found "
                    "in database."
                )

            return "\n---\n".join(
                self._phone_to_document(phone)
                for phone in phones
            )

    # ---------------------------------------------------------
    # SEMANTIC RAG
    # ---------------------------------------------------------

    def retrieve(
        self,
        query: str,
        top_k: int = 4,
    ) -> str:
        """Retrieve relevant phone information using semantic search."""

        lower_query = query.lower()

        # Ranking query
        if (
            "best battery" in lower_query
            or "highest battery" in lower_query
            or "longest battery" in lower_query
        ):
            return self.retrieve_best_battery()

        # Semantic search
        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
        )

        retrieved_docs = (
            results.get("documents", [[]])[0]
            if results
            else []
        )

        if not retrieved_docs:
            return (
                "No matching Samsung phone data "
                "found in database."
            )

        return "\n---\n".join(retrieved_docs)