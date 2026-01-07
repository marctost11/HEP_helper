from langchain_openai import ChatOpenAI

def get_llm():
    return ChatOpenAI(
        model="gpt-4o",
        temperature=0.2,
        # Helps avoid TPM blowups from very large completions.
        # (TPM counts input + output tokens.)
        #max_tokens=1500,
    )
