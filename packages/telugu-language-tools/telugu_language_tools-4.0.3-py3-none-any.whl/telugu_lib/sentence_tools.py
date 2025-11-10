"""
Sentence similarity and correction tools for Telugu text.

This module provides functionality to find similar Telugu sentences
and correct grammar/spelling using SentenceTransformers.
"""

try:
    from sentence_transformers import SentenceTransformer, util
    import torch
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

# Preload the model (lightweight multilingual model)
_MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
_model = None


def _get_model():
    """
    Lazy load the sentence transformer model.
    Returns the cached model or loads it if not already loaded.
    """
    global _model
    if _model is None:
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not installed. "
                "Please install it with: pip install sentence-transformers"
            )
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


def find_similar_sentence(query, reference_list, top_k=1, min_score=0.5):
    """
    Find the most similar sentence(s) from a list of references.

    Args:
        query (str): The query sentence in Telugu
        reference_list (list): List of Telugu reference sentences
        top_k (int): Number of top similar sentences to return (default: 1)
        min_score (float): Minimum similarity score threshold (default: 0.5)

    Returns:
        tuple: (best_sentence, similarity_score) if top_k=1
        list: List of tuples [(sentence, score), ...] if top_k > 1

    Example:
        >>> refs = ["వర్షం పడుతోంది", "ఇప్పుడు వాన వస్తోంది", "నేను తినడానికి వెళ్తున్నాను"]
        >>> sentence, score = find_similar_sentence("వర్షం కురుస్తోంది", refs)
        >>> print(sentence, score)
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError(
            "sentence-transformers is required for this feature. "
            "Install it with: pip install sentence-transformers"
        )

    if not reference_list:
        return (None, 0.0) if top_k == 1 else []

    model = _get_model()

    # Encode the query and reference sentences
    query_emb = model.encode(query, convert_to_tensor=True)
    ref_emb = model.encode(reference_list, convert_to_tensor=True)

    # Compute cosine similarity
    scores = util.cos_sim(query_emb, ref_emb)[0]

    # Find top-k most similar sentences
    top_results = []
    for score, sentence in sorted(zip(scores, reference_list), reverse=True)[:top_k]:
        if float(score) >= min_score:
            top_results.append((sentence, float(score)))

    if not top_results:
        # Return the best match even if below threshold
        best_idx = torch.argmax(scores).item()
        best_score = float(scores[best_idx])
        if top_k == 1:
            return (reference_list[best_idx], best_score)
        else:
            return [(reference_list[best_idx], best_score)]

    if top_k == 1:
        return (top_results[0][0], top_results[0][1])
    return top_results


def correct_sentence(query, references, min_score=0.5):
    """
    Correct a Telugu sentence by finding the best matching reference.

    Args:
        query (str): The potentially incorrect Telugu sentence
        references (list): List of correct Telugu sentences to match against
        min_score (float): Minimum similarity score threshold

    Returns:
        tuple: (corrected_sentence, similarity_score)

    Example:
        >>> refs = ["నేను ఇంటికి వెళ్తున్నాను", "వర్షం పడుతోంది", "ఇది మంచి పుస్తకం"]
        >>> corrected, score = correct_sentence("వర్షం పడుతునది", refs)
        >>> print(corrected, score)
    """
    return find_similar_sentence(query, references, top_k=1, min_score=min_score)


def rank_sentences(query, reference_list, min_score=0.3):
    """
    Rank all reference sentences by similarity to the query.

    Args:
        query (str): The query sentence in Telugu
        reference_list (list): List of Telugu reference sentences
        min_score (float): Minimum similarity score to include in results

    Returns:
        list: Sorted list of tuples [(sentence, score), ...] in descending order

    Example:
        >>> refs = ["వర్షం పడుతోంది", "ఇప్పుడు వాన వస్తోంది", "నేను తినడానికి వెళ్తున్నాను"]
        >>> ranked = rank_sentences("వర్షం కురుస్తోంది", refs)
        >>> for sentence, score in ranked:
        ...     print(f"{sentence}: {score:.3f}")
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError(
            "sentence-transformers is required for this feature. "
            "Install it with: pip install sentence-transformers"
        )

    if not reference_list:
        return []

    model = _get_model()

    # Encode all sentences
    query_emb = model.encode(query, convert_to_tensor=True)
    ref_emb = model.encode(reference_list, convert_to_tensor=True)

    # Compute similarities
    scores = util.cos_sim(query_emb, ref_emb)[0]

    # Create and sort results
    results = [(ref, float(score))
               for ref, score in zip(reference_list, scores)
               if float(score) >= min_score]

    # Sort by score in descending order
    results.sort(key=lambda x: x[1], reverse=True)

    return results


def batch_similarity(queries, reference_list, batch_size=32):
    """
    Compute similarity for multiple queries against the reference list.

    Args:
        queries (list): List of query sentences
        reference_list (list): List of reference sentences
        batch_size (int): Batch size for encoding (default: 32)

    Returns:
        list: List of tuples (query, best_match, best_score) for each query

    Example:
        >>> queries = ["వర్షం కురుస్తోంది", "నేను వస్తున్నాను"]
        >>> refs = ["వర్షం పడుతోంది", "నేను ఇంటికి వెళ్తున్నాను"]
        >>> results = batch_similarity(queries, refs)
        >>> for query, match, score in results:
        ...     print(f"{query} -> {match} ({score:.3f})")
    """
    if not SENTENCE_TRANSFORMERS_AVAILABLE:
        raise ImportError(
            "sentence-transformers is required for this feature. "
            "Install it with: pip install sentence-transformers"
        )

    if not queries or not reference_list:
        return []

    model = _get_model()

    # Encode all queries
    query_embeddings = model.encode(queries, convert_to_tensor=True, batch_size=batch_size)
    ref_embeddings = model.encode(reference_list, convert_to_tensor=True, batch_size=batch_size)

    # Compute similarities
    similarity_matrix = util.cos_sim(query_embeddings, ref_embeddings)

    results = []
    for i, query in enumerate(queries):
        scores = similarity_matrix[i]
        best_idx = torch.argmax(scores).item()
        best_score = float(scores[best_idx])
        results.append((query, reference_list[best_idx], best_score))

    return results


def is_sentence_transformers_available():
    """
    Check if sentence-transformers library is available.

    Returns:
        bool: True if sentence-transformers is installed, False otherwise
    """
    return SENTENCE_TRANSFORMERS_AVAILABLE
