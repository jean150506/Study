import math
from pathlib import Path

import matplotlib.pyplot as plt


def cosine_similarity(a, b):
    """Calcula a similaridade por cosseno entre dois vetores."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def encode_text_to_numbers(text: str):
    """Exemplo toy de codificação de texto em números.

    A ideia aqui é simplificada: cada letra vira um valor de acordo com
    a posição no alfabeto. Exemplo: a -> 1, b -> 2, c -> 3.
    Assim, a palavra 'abc' vira [1, 2, 3], que pode ser interpretada
    como coordenadas de um ponto em um espaço tridimensional.
    """
    text = text.lower()
    values = []
    for char in text:
        if char.isalpha():
            values.append(ord(char) - ord("a") + 1)
        else:
            values.append(0)
    return values


def plot_text_encoding():
    """Mostra visualmente a ideia toy de transformar texto em coordenadas."""
    sample_text = "abc"
    coords = encode_text_to_numbers(sample_text)
    if len(coords) < 3:
        coords += [0] * (3 - len(coords))

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, projection="3d")

    ax.scatter(coords[0], coords[1], coords[2], s=220, color="#8e24aa", edgecolor="black", zorder=5)
    ax.plot([0, coords[0]], [0, coords[1]], [0, coords[2]], color="#8e24aa", alpha=0.5, linewidth=2)

    ax.set_title("Exemplo toy: texto -> números -> coordenadas")
    ax.set_xlabel("Coordenada X")
    ax.set_ylabel("Coordenada Y")
    ax.set_zlabel("Coordenada Z")
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 4)
    ax.set_zlim(0, 4)
    ax.text(coords[0], coords[1], coords[2], f"({coords[0]}, {coords[1]}, {coords[2]})",
            fontsize=10, color="darkviolet", fontweight="bold")
    ax.text2D(0.02, 0.98, f"Texto: {sample_text}\nMapa: a=1, b=2, c=3\nResultado: {coords}",
              transform=ax.transAxes, fontsize=10, va="top",
              bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8})

    fig.tight_layout()
    fig.savefig(Path(__file__).with_name("codificacao_texto_em_coordenadas.png"), dpi=220, bbox_inches="tight")


def build_example():
    """Cria um exemplo didático de textos, vetores e pergunta."""
    texts = {
        "doc_aws": "Como configurar uma Knowledge Base na AWS?",
        "doc_lambda": "Como criar uma função Lambda em Python?",
        "doc_vetores": "O que são embeddings e vetores semânticos?",
        "doc_banco": "Como criar um banco de dados relacional?",
        "doc_bolo": "Receita de bolo de chocolate simples",
    }

    # Vetores escolhidos manualmente para ilustrar proximidade semântica.
    # A pergunta abaixo está mais próxima de "doc_vetores" e "doc_aws".
    vectors = {
        "doc_aws": [0.95, 0.15],
        "doc_lambda": [0.15, 0.95],
        "doc_vetores": [0.82, 0.78],
        "doc_banco": [0.20, 0.10],
        "doc_bolo": [-0.70, -0.60],
    }

    question = "Como funciona a busca por similaridade em uma Knowledge Base vetorial?"
    query_vector = [0.84, 0.75]

    return texts, vectors, query_vector, question


def plot_demo(texts, vectors, query_vector, question):
    """Gera gráficos explicativos e salva em arquivo PNG."""
    similarities = []
    labels = []
    for name, vector in vectors.items():
        score = cosine_similarity(query_vector, vector)
        similarities.append((name, score))
        labels.append(name)

    sorted_scores = sorted(similarities, key=lambda item: item[1], reverse=True)

    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Gráfico 1: espaço vetorial.
    ax = axes[0]
    ax.axhline(0, color="gray", lw=0.7, alpha=0.6)
    ax.axvline(0, color="gray", lw=0.7, alpha=0.6)

    # Desenha os pontos e suas setas do origem.
    for name, vector in vectors.items():
        x, y = vector
        color = "#1f77b4"
        if name == sorted_scores[0][0]:
            color = "#2ca02c"
        ax.scatter(x, y, s=140, color=color, edgecolor="black", zorder=3)
        ax.annotate(name, (x, y), xytext=(6, 6), textcoords="offset points", fontsize=9)
        ax.arrow(0, 0, x, y, head_width=0.04, head_length=0.05, length_includes_head=True,
                 color=color, alpha=0.35, linewidth=1.2)

    ax.scatter(query_vector[0], query_vector[1], s=220, color="red", marker="X", zorder=4)
    ax.annotate("Pergunta", (query_vector[0], query_vector[1]), xytext=(8, 8), textcoords="offset points",
                fontsize=10, fontweight="bold", color="red")

    ax.set_title("Espaço vetorial: cada texto vira um ponto")
    ax.set_xlabel("Eixo 1")
    ax.set_ylabel("Eixo 2")
    ax.set_xlim(-1.0, 1.1)
    ax.set_ylim(-1.0, 1.1)
    ax.grid(True, alpha=0.25)
    ax.text(
        0.02, 0.98,
        "A pergunta também vira um vetor.\n"
        "Textos próximos têm significado parecido.\n"
        "Exemplo: similaridade por cosseno",
        transform=ax.transAxes,
        verticalalignment="top",
        fontsize=9.5,
        bbox={"boxstyle": "round", "facecolor": "white", "alpha": 0.8},
    )

    # Gráfico 2: barras de similaridade.
    ax2 = axes[1]
    names = [item[0] for item in sorted_scores]
    values = [item[1] for item in sorted_scores]

    colors = ["#2ca02c" if i < 2 else "#1f77b4" for i in range(len(values))]
    ax2.bar(names, values, color=colors, edgecolor="black")
    ax2.axhline(0.7, color="red", linestyle="--", linewidth=1.2, label="limiar de relevância")
    ax2.set_ylim(0, 1.05)
    ax2.set_title("Pontuação de similaridade com a pergunta")
    ax2.set_ylabel("Score de similaridade")
    ax2.set_xticklabels(names, rotation=20, ha="right")
    ax2.grid(axis="y", alpha=0.25)
    ax2.legend()

    fig.suptitle("Como uma Knowledge Base vetorial encontra textos semelhantes", fontsize=16, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.96])

    output_path = Path(__file__).with_name("demonstracao_kb_vetores.png")
    plt.savefig(output_path, dpi=220, bbox_inches="tight")
    plt.show()
    return output_path


def print_explanation(texts, vectors, query_vector, question):
    print("=" * 80)
    print("DEMONSTRAÇÃO DIDÁTICA: VETORES EM UMA KNOWLEDGE BASE")
    print("=" * 80)
    print()
    print("1) O texto não é comparado literalmente por palavras.")
    print("   Em vez disso, cada texto vira um vetor em um espaço multidimensional.")
    print()
    print("2) A pergunta também vira um vetor.")
    print("   Então a busca compara a posição da pergunta com a posição dos documentos.")
    print()
    print("3) O critério usado aqui é a similaridade por cosseno:")
    print("   cos(theta) = (A · B) / (|A| * |B|)")
    print("   Quanto mais próximo de 1, mais semelhantes são os conceitos.")
    print()
    print("4) Pergunta de exemplo:")
    print(f"   {question}")
    print()
    print("5) Exemplo toy de como um texto vira números:")
    sample_text = "abc"
    encoded = encode_text_to_numbers(sample_text)
    print(f"   Texto: {sample_text}")
    print("   Mapeamento simplificado: a=1, b=2, c=3")
    print(f"   Resultado numérico: {encoded}")
    print("   Isso pode ser interpretado como um ponto em um espaço dimensional:")
    print(f"   Coordenadas: ({encoded[0]}, {encoded[1]}, {encoded[2]})")
    print()
    print("6) Textos de exemplo e seus vetores:")
    for name, vector in vectors.items():
        print(f"   - {name}: {texts[name]} => vetor {vector}")
    print()
    print("7) Vetor da pergunta:")
    print(f"   {query_vector}")
    print()
    print("8) Resultado da busca por similaridade:")
    similarities = []
    for name, vector in vectors.items():
        score = cosine_similarity(query_vector, vector)
        similarities.append((name, score))

    for name, score in sorted(similarities, key=lambda item: item[1], reverse=True):
        print(f"   - {name}: score = {score:.3f}")
    print()
    print("9) Interpretação prática:")
    print("   - Pontuações altas indicam que o texto está semanticamente próximo da pergunta.")
    print("   - Pontuações baixas indicam que o conteúdo é mais distante do tema.")
    print("   - Isso é exatamente o que uma Knowledge Base vetorial faz para recuperar informação.")
    print()
    print("10) Observação importante:")
    print("   Na prática, esses vetores são gerados automaticamente por modelos de embedding")
    print("   e não são definidos manualmente como neste exemplo didático.")
    print("=" * 80)


def main():
    texts, vectors, query_vector, question = build_example()
    print_explanation(texts, vectors, query_vector, question)
    output_path = plot_demo(texts, vectors, query_vector, question)
    plot_text_encoding()
    print(f"\nGráfico salvo em: {output_path}")
    print("Gráfico de codificação salvo em: C:/Users/Jean/Desktop/Scripts/study_programs/Study/terraform_study/scripts_para_entendimento/codificacao_texto_em_coordenadas.png")


if __name__ == "__main__":
    main()
