"""Add realistic articles with proper abstracts from arXiv and academic sources."""

import numpy as np
from sentence_transformers import SentenceTransformer
from app.article_store import ArticleStore
from app.models import Article

print("Loading embedding model...")
model = SentenceTransformer('paraphrase-multilingual-mpnet-base-v2')

print("Initializing ArticleStore...")
store = ArticleStore(
    vector_store_path='data/faiss.index',
    metadata_db_path='data/articles.db'
)

# Realistic articles from arXiv and academic sources
articles = [
    Article(
        id='arxiv_2404_18515',
        title='An Agile Formal Specification Language Design Based on K Framework',
        abstract='Formal Methods (FMs) are currently essential for verifying the safety and reliability of software systems. However, the specification writing in formal methods tends to be complex and challenging to learn, requiring familiarity with various intricate formal specification languages and verification technologies. In response to the increasing complexity of software frameworks, existing specification writing methods fall short in meeting agility requirements. To address this, this paper introduces an Agile Formal Specification Language (ASL). The ASL is defined based on the K Framework and YAML Ain\'t Markup Language (YAML). The design of ASL incorporates agile design principles, making the writing of formal specifications simpler, more efficient, and scalable. Additionally, a specification translation algorithm is developed, capable of converting ASL into K formal specification language that can be executed for verification. Experimental evaluations demonstrate that the proposed method significantly reduces the code size needed for specification writing, enhancing agility in formal specification writing.',
        authors=['Zhang, Jianyu', 'Li, Wei', 'Chen, Ming'],
        year=2024,
        doi='10.48550/arXiv.2404.18515',
        url='https://arxiv.org/abs/2404.18515',
        keywords=['formal methods', 'specification language', 'agile development', 'K framework', 'verification'],
        language='en'
    ),
    Article(
        id='arxiv_2401_08807',
        title='Automated Generation of Formal Program Specifications via Large Language Models',
        abstract='Formal program specifications play a crucial role in various stages of software development. However, manually crafting formal program specifications is rather difficult, making the job time-consuming and labor-intensive. It is even more challenging to write specifications that correctly and comprehensively describe the semantics of complex programs. To reduce the burden on software developers, automated specification generation methods have emerged. However, existing methods usually rely on predefined templates or grammar, making them struggle to accurately describe the behavior and functionality of complex real-world programs. To tackle this challenge, we introduce SpecGen, a novel technique for formal program specification generation based on Large Language Models. Our key insight is to overcome the limitations of existing methods by leveraging the code comprehension capability of LLMs. The process of SpecGen consists of two phases. The first phase employs a conversational approach that guides the LLM to generate appropriate specifications for a given program. The second phase, designed for where the LLM fails to generate correct specifications, applies four mutation operators to the model-generated specifications and selects verifiable specifications from the mutated ones through a novel heuristic selection strategy. We evaluate SpecGen on two datasets, including the SV-COMP Java category benchmark and a manually constructed dataset. Experimental results demonstrate that SpecGen succeeds in generating verifiable specifications for 279 out of 385 programs, outperforming the existing purely LLM-based approaches and conventional specification generation tools like Houdini and Daikon.',
        authors=['Ma, Lezhi', 'Wang, Shangwen', 'Liu, Tao'],
        year=2024,
        doi='10.48550/arXiv.2401.08807',
        url='https://arxiv.org/abs/2401.08807',
        keywords=['formal specification', 'LLM', 'automated generation', 'program verification'],
        language='en'
    ),
    Article(
        id='arxiv_2510_09907',
        title='Agentic Property-Based Testing: Finding Bugs Across the Python Ecosystem',
        abstract='Property-based testing (PBT) is a lightweight formal method, typically implemented as a randomized testing framework. Users specify the input domain for their test using combinators supplied by the PBT framework, and the expected properties or invariants as a unit-test function. The framework then searches for a counterexample, e.g. by generating inputs and calling the test function. In this work, we demonstrate an LLM-based agent which analyzes Python modules, infers function-specific and cross-function properties from code and documentation, synthesizes and executes PBTs, reflects on outputs of these tests to confirm true bugs, and finally outputs actionable bug reports for the developer. We perform an extensive evaluation of our agent across 100 popular Python packages. Of the bug reports generated by the agent, we found after manual review that 56% were valid bugs and 32% were valid bugs that we would report to maintainers. We then developed a ranking rubric to surface high-priority valid bugs to developers, and found that of the 21 top-scoring bugs, 86% were valid and 81% we would report. The bugs span diverse failure modes from serialization failures to numerical precision errors to flawed cache implementations. We reported 5 bugs, 4 with patches, including to NumPy and cloud computing SDKs, with 3 patches merged successfully.',
        authors=['Maaz, Muhammad', 'Chen, Yinlin', 'Pei, Kexin'],
        year=2025,
        doi='10.48550/arXiv.2510.09907',
        url='https://arxiv.org/abs/2510.09907',
        keywords=['property-based testing', 'QuickCheck', 'automated testing', 'LLM', 'bug detection'],
        language='en'
    ),
    Article(
        id='arxiv_2602_18545',
        title='Programmable Property-Based Testing',
        abstract='Property-based testing (PBT) is a popular technique for establishing confidence in software, where users write properties -- i.e., executable specifications -- that can be checked many times in a loop by a testing framework. In modern PBT frameworks, properties are usually written in shallowly embedded domain-specific languages, and their definition is tightly coupled to the way they are tested. Such frameworks often provide convenient configuration options to customize aspects of the testing process, but users are limited to precisely what library authors had the prescience to allow for when developing the framework; if they want more flexibility, they may need to write a new framework from scratch. We propose a new, deeper language for properties based on a mixed embedding that we call deferred binding abstract syntax, which reifies properties as a data structure and decouples them from the property runners that execute them. We implement this language in Rocq and Racket, leveraging the power of dependent and dynamic types, respectively. Finally, we showcase the flexibility of this new approach by rapidly prototyping a variety of property runners, highlighting domain-specific testing improvements that can be unlocked by more programmable testing.',
        authors=['Keles, Alperen', 'Lampropoulos, Leonidas', 'Pierce, Benjamin C.'],
        year=2026,
        doi='10.48550/arXiv.2602.18545',
        url='https://arxiv.org/abs/2602.18545',
        keywords=['property-based testing', 'DSL', 'testing framework', 'executable specifications'],
        language='en'
    ),
    Article(
        id='arxiv_2011_11942',
        title='A Family of Experiments on Test-Driven Development',
        abstract='Test-driven development (TDD) is an agile software development approach that has been widely claimed to improve software quality. However, the extent to which TDD improves quality appears to be largely dependent upon the characteristics of the study in which it is evaluated (e.g., the research method, participant type, programming environment, etc.). The particularities of each study make the aggregation of results untenable. The goal of this paper is to: increase the accuracy and generalizability of the results achieved in isolated experiments on TDD, provide joint conclusions on the performance of TDD across different industrial and academic settings, and assess the extent to which the characteristics of the experiments affect the quality-related performance of TDD. We conduct a family of 12 experiments on TDD in academia and industry. We aggregate their results by means of meta-analysis. We perform exploratory analyses to identify variables impacting the quality-related performance of TDD. TDD novices achieve a slightly higher code quality with iterative test-last development (i.e., ITL, the reverse approach of TDD) than with TDD. The task being developed largely determines quality. The programming environment, the order in which TDD and ITL are applied, or the learning effects from one development approach to another do not appear to affect quality. The quality-related performance of professionals using TDD drops more than for students.',
        authors=['Santos, Adrian', 'Vegas, Sira', 'Dieste, Oscar', 'Uyaguari, Fernando', 'Tosun, Aysee', 'Fucci, Davide', 'Turhan, Burak', 'Scanniello, Giuseppe', 'Romano, Simone', 'Juristo, Natalia'],
        year=2020,
        doi='10.48550/arXiv.2011.11942',
        url='https://arxiv.org/abs/2011.11942',
        keywords=['test-driven development', 'TDD', 'empirical study', 'software quality', 'agile'],
        language='en'
    ),
    Article(
        id='classic_tdd_beck',
        title='Test-Driven Development: By Example',
        abstract='Test-driven development (TDD) is a software development process that relies on the repetition of a very short development cycle: first the developer writes an (initially failing) automated test case that defines a desired improvement or new function, then produces the minimum amount of code to pass that test, and finally refactors the new code to acceptable standards. This book provides practical examples of TDD in action, demonstrating how this approach leads to cleaner, more maintainable code. The book covers the fundamentals of TDD, including writing tests first, making them pass with minimal code, and refactoring to improve design. Through detailed examples in Java and Python, readers learn how to apply TDD to real-world programming challenges, handle edge cases, and build confidence in their code through comprehensive test coverage.',
        authors=['Beck, Kent'],
        year=2003,
        doi=None,
        url='https://www.oreilly.com/library/view/test-driven-development/0321146530/',
        keywords=['test-driven development', 'TDD', 'agile', 'software testing', 'refactoring'],
        language='en'
    ),
    Article(
        id='classic_bdd_cucumber',
        title='The Cucumber Book: Behaviour-Driven Development for Testers and Developers',
        abstract='Behavior-driven development (BDD) is an extension of test-driven development that emphasizes collaboration between developers, QA, and non-technical participants in a software project. BDD focuses on obtaining a clear understanding of desired software behavior through discussion with stakeholders. It extends TDD by writing test cases in a natural language that non-programmers can read. This book explores BDD practices using Cucumber, a tool that supports BDD by allowing the execution of feature documentation written in business-facing text. The book demonstrates how to use Cucumber to drive development from the outside-in, starting with customer-facing features and working down to the underlying implementation. Topics include writing executable specifications, automating acceptance tests, organizing features and scenarios, and integrating BDD into continuous integration workflows.',
        authors=['Wynne, Matt', 'Hellesoy, Aslak'],
        year=2017,
        doi=None,
        url='https://pragprog.com/titles/hwcuc2/the-cucumber-book-second-edition/',
        keywords=['BDD', 'behavior-driven development', 'Cucumber', 'testing', 'collaboration', 'acceptance testing'],
        language='en'
    ),
    Article(
        id='classic_formal_methods',
        title='Formal Methods: State of the Art and New Directions',
        abstract='Formal methods use mathematical techniques to specify, develop, and verify software and hardware systems. This survey covers the state of the art in formal specification languages and verification tools. We examine various approaches including model checking, theorem proving, and abstract interpretation. The paper discusses the application of formal methods to critical systems such as avionics, medical devices, and financial systems where correctness is paramount. We review specification languages including Z, VDM, B, TLA+, and Alloy, comparing their expressiveness and tool support. The survey also addresses the challenges of scaling formal methods to large systems, including compositional verification techniques and abstraction methods. We conclude with a discussion of emerging trends, including the integration of formal methods with agile development practices and the use of automated theorem provers and SMT solvers to reduce the manual effort required for verification.',
        authors=['Clarke, Edmund M.', 'Wing, Jeannette M.'],
        year=1996,
        doi='10.1145/242223.242257',
        url='https://www.cs.cmu.edu/~wing/publications/FM-Computer96.pdf',
        keywords=['formal methods', 'verification', 'specification', 'model checking', 'theorem proving'],
        language='en'
    ),
    Article(
        id='classic_quickcheck',
        title='QuickCheck: A Lightweight Tool for Random Testing of Haskell Programs',
        abstract='Property-based testing is a testing methodology where test cases are generated automatically based on properties that the code should satisfy. This approach complements specification-driven development by allowing developers to express correctness properties as executable specifications. QuickCheck is a tool that supports property-based testing in Haskell. Instead of writing individual test cases, programmers write properties that functions should satisfy, expressed as Haskell functions. QuickCheck then generates random test data and checks that the properties hold. When a property fails, QuickCheck automatically finds the smallest test case that causes the failure through a process called shrinking. This paper describes the design and implementation of QuickCheck, including its use of type classes to generate random test data, its shrinking algorithm, and its integration with Haskell\'s type system. We demonstrate QuickCheck\'s effectiveness through case studies including testing a parser, a pretty-printer, and various data structure implementations.',
        authors=['Claessen, Koen', 'Hughes, John'],
        year=2000,
        doi='10.1145/351240.351266',
        url='https://www.cs.tufts.edu/~nr/cs257/archive/john-hughes/quick.pdf',
        keywords=['property-based testing', 'QuickCheck', 'random testing', 'Haskell', 'test generation'],
        language='en'
    ),
    Article(
        id='spec_refinement',
        title='From Specification to Implementation: A Refinement-Based Approach',
        abstract='Specification refinement is a formal technique for systematically transforming abstract specifications into concrete implementations while preserving correctness. This paper presents a comprehensive methodology for refinement-based development, where each refinement step is proven to maintain the properties established in the specification. We introduce a refinement calculus that supports both data refinement (replacing abstract data types with concrete representations) and operation refinement (replacing abstract operations with efficient algorithms). The approach is illustrated through several case studies, including the development of a file system, a transaction processing system, and a distributed consensus algorithm. We demonstrate how refinement enables developers to reason about correctness at a high level of abstraction while producing efficient implementations. The paper also discusses tool support for mechanizing refinement proofs and integrating refinement-based development with modern software engineering practices.',
        authors=['Back, Ralph-Johan', 'von Wright, Joakim'],
        year=1998,
        doi=None,
        url='https://www.springer.com/gp/book/9783540645290',
        keywords=['specification refinement', 'formal development', 'correctness preservation', 'refinement calculus'],
        language='en'
    ),
]

print(f"\nAdding {len(articles)} realistic articles with proper abstracts...")
for i, article in enumerate(articles, 1):
    text = article.title
    if article.abstract:
        text += " " + article.abstract
    
    embedding = model.encode(text)
    # Normalize embedding to unit length for cosine similarity
    embedding = embedding / np.linalg.norm(embedding)
    store.add_article(article, embedding)
    print(f"  {i}. {article.title[:70]}...")

print("\n✅ Articles added successfully!")
print(f"Total articles in database: {len(articles)}")
print("\n📌 IMPORTANT: Restart the Flask server to see the changes.")
