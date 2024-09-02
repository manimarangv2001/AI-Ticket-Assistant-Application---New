import os
from langchain_chroma import Chroma
from azure_openai.configure_openai import model, embedding_function
from langchain.docstore.document import Document
from azure_openai.prompts import fetchDescribe

def formatter(docs):
    result = []
    for doc in docs:
        metadata = doc[0].metadata
        metadata['description'] = fetchDescribe(doc[0].page_content)
        metadata['relavent_score'] = doc[1]
        metadata['page_content'] = doc[0].page_content
        result.append(metadata)
    return result


def find_similar_catalog_item(query):
    CATALOGITEMDOCS = "Document_Store\\catalog_item_db"
    dir_path = os.path.join(os.getcwd(), CATALOGITEMDOCS)
    isdir = os.path.isdir(dir_path)
    if(isdir):
        db3 = Chroma(persist_directory=dir_path, embedding_function=embedding_function)
        docs = db3.similarity_search_with_relevance_scores(query, 4)
        return docs
    else:
        print("catalog_item_db not exist.")


def find_similar_kb_articles(query):
    KBARTICLESDOCS = "Document_Store\\kb_articles_db"
    dir_path = os.path.join(os.getcwd(), KBARTICLESDOCS)
    isdir = os.path.isdir(dir_path)
    if(isdir):
        # load from disk
        db3 = Chroma(persist_directory=dir_path, embedding_function=embedding_function)
        docs = db3.similarity_search_with_relevance_scores(query, 4)
        # print(docs)
        return docs
    else:
        print("kb_articles_db not exist.")

async def checkSimilarity(query):
    similar_catalog_items = formatter(find_similar_catalog_item(query))
    return similar_catalog_items