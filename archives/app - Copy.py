from ollama import chat

response=chat(
    model="gemma3:4b",
    messages=[
        {
          "role":"system",
          "content":"You are a mathematics teacher"
        },
	{
          "role":"user",
          "content":"Explain Pythagoras Theorem"
        },

       ]
    )

#print(response['message']['content'])
print(response)