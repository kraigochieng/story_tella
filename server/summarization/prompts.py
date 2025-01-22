from langchain_core.prompts import ChatPromptTemplate, FewShotChatMessagePromptTemplate

map_example_prompt = ChatPromptTemplate.from_messages(
    [
        ("human", "{context}"),
        ("ai", "{output}"),
    ]
)

map_examples = [
    {
        "context": """
            Ole Kaelo's pride was wounded. How could the
            old fellow think he was so naive as not to know how to
            organise his sales? Perhaps, he thought sourly, his
            clansmate had not known that in his earlier years in
            Agribix, he had been sent out to open sales depots in
            remote places which he quickly developed into
            expanding profitable modern branches. Maybe it was
            time he showed the ageing businessman that younger
            bulls were raring to go and the old ones would better
            start skirting the pastures. He threw caution to the wind.
        """,
        "output": """
            Ole Kaelo's pride was hurt by the older businessman.
            This is because Ole Kaelo wondered how the old businessman
            did not believe he was good at sales even though Ole Kaelo worked in sales depots while 
            in Agribix. 
        """,
    }
]

map_few_shot_prompt = FewShotChatMessagePromptTemplate(
    example_prompt=map_example_prompt, examples=map_examples
)


map_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
                You will communicate in very simple and concise language
            """,
        ),
        map_few_shot_prompt,
        (
            "human",
            """

            Write a concise summary of the following ensuring you bring out the characters and themes:

            {context}
            """,
        ),
        # (
        #     "human",
        #     """
        #     The following is a set of documents:
        #     {docs}
        #     Based on this list of docs, please identify the main themes
        #     Helpful Answer:
        #     """,
        # ),
    ]
)


reduce_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "human",
            """
        
            The following is a set of summaries:
            
            {docs}

            Take these and distill it into a final, consolidated summary ensuring you mention the family characters.
            Please make the summary like a flowing story moving from one idea to another.
            

                        Please touch one each summary in the set in s
            """,
        )
    ]
)
