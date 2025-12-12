from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.edmundson import EdmundsonSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words
from .models import State


def run_edmundson(text: str, sentence_count: int) -> str:
    if not text.strip(): return ""
    if sentence_count < 1: sentence_count = 1
    
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = EdmundsonSummarizer(Stemmer("english"))
    summarizer.stop_words = get_stop_words("english")
    summarizer.null_words = get_stop_words("english")
    summarizer.bonus_words = ["significant", "important", "key", "main"]
    summarizer.stigma_words = ["example", "maybe"]

    try:
        summary_sentences = summarizer(parser.document, sentence_count)
        return " ".join([str(s) for s in summary_sentences])
    except:
        return text # Fallback if text is too short


def split_text_func(state: State) -> dict:
    text = state.original_text
    mid = len(text) // 2
    split_point = text.find(' ', mid)
    
    if split_point == -1: 
        chunks = [text]
    else:
        chunks = [text[:split_point], text[split_point:]]
        
    return {
        "chunks": chunks,
        "logs": state.logs + [f"Step 1: Split text into {len(chunks)} chunks."]
    }

def summarize_chunks_func(state: State) -> dict:
    summaries = []
    for i, chunk in enumerate(state.chunks):
        s = run_edmundson(chunk, 2)
        summaries.append(s)
        
    return {
        "summaries": summaries,
        "logs": state.logs + [f"Step 2: Generated {len(summaries)} chunk summaries."]
    }

def merge_summaries_func(state: State) -> dict:
    merged = " ".join(state.summaries)
    
    start_count = 4
    
    return {
        "current_summary": merged,
        "iteration_count": start_count,
        "logs": state.logs + ["Step 3: Merged summaries."]
    }

def refine_summary_func(state: State) -> dict:
    current_count = state.iteration_count
    new_count = max(1, current_count - 1)
    
    refined_text = run_edmundson(state.current_summary, new_count)

    return {
        "current_summary": refined_text,
        "iteration_count": new_count,
        "logs": state.logs + [f"Step 4: Refined summary to {new_count} sentences."]
    }

TOOL_REGISTRY = {
    "split": split_text_func,
    "summarize_chunks": summarize_chunks_func,
    "merge": merge_summaries_func,
    "refine": refine_summary_func
}