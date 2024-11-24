from ollama import chat
from ollama import ChatResponse

from simplelog import log as dbgln

def parse(text, info):

    prompts = {
        "date": f"Com base no texto abaixo, retorne a data em que essa transação aconteceu no formato"
                f"ANO-MÊS-DIA. É importantíssimo e urgente que retorne apenas nesse formato."
                f"Não retorne nenhum texto adicional além da data solicitada.",
        "amount": f"Com base no texto abaixo, retorne o valor dessa transação."
                  f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                  f"Não retorne nenhum texto adicional além do valor solicitado."
                  f"Não retorne ponto final no texto.",
        "bank": f"Com base no texto abaixo, retorne o nome do banco ou da instiuição onde ocorreu essa transação."
                f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                f"Não retorne nenhum texto adicional além do nome solicitado."
                f"Não retorne ponto final no texto.",
        "person1": f"Você está fazendo o reconhecimento de texto de uma imagem."
                   f"Com base no texto abaixo, retorne o nome de quem enviou o dinheiro nessa transação."
                   f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                   f"Não retorne nenhum texto adicional além do nome solicitado.",
        "person2": f"Você está fazendo o reconhecimento de texto de um comprovante de transferência."
                   f"Com base no texto abaixo, retorne o nome de quem recebeu o dinheiro nessa transação."
                   f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                   f"Não retorne nenhum texto adicional além do nome solicitado.",
        "description": f"O que está escrito nesse texto?"
                       f"É importantíssimo e urgente que retorne apenas essa informação e nada mais."
                       f"Não retorne nenhum texto adicional além da descrição solicitada."
    }

    model = ["llama3.2:1b", "llama3.2"]

    response: ChatResponse = chat(model=model[1], messages=[
        {
            'role': 'user',
            'content': f"{prompts[info]}\n\n{text}",
        },
    ])

    answer = response['message']['content']

    dbgln(f"String for '{info}' found using AI: '{answer}'.")
    return answer
