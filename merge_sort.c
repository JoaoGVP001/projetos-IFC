#include <stdio.h>

void merge(int v[], int inicio, int meio, int fim) {
    int n1 = meio - inicio + 1;
    int n2 = fim - meio;

    int esquerda[n1];
    int direita[n2];

    for (int i = 0; i < n1; i++)
        esquerda[i] = v[inicio + i];

    for (int i = 0; i < n2; i++)
        direita[i] = v[meio + 1 + i];

    int i = 0, j = 0, k = inicio;

    while (i < n1 && j < n2) {
        if (esquerda[i] <= direita[j]) {
            v[k] = esquerda[i];
            i++;
        } else {
            v[k] = direita[j];
            j++;
        }
        k++;
    }

    while (i < n1) {
        v[k] = esquerda[i];
        i++;
        k++;
    }

    while (j < n2) {
        v[k] = direita[j];
        j++;
        k++;
    }
}

void mergeSort(int v[], int inicio, int fim) {
    if (inicio < fim) {
        int meio = (inicio + fim) / 2;

        mergeSort(v, inicio, meio);
        mergeSort(v, meio + 1, fim);

        merge(v, inicio, meio, fim);
    }
}

int main() {
    int n;

    printf("Quantos valores deseja ordenar? ");
    scanf("%d", &n);

    int vetor[n];

    printf("Digite os %d valores separados por espaco:\n", n);

    for (int i = 0; i < n; i++)
        scanf("%d", &vetor[i]);

    printf("\nVetor original:\n");

    for (int i = 0; i < n; i++)
        printf("%d ", vetor[i]);

    printf("\n");

    mergeSort(vetor, 0, n - 1);

    printf("\nVetor ordenado:\n");

    for (int i = 0; i < n; i++)
        printf("%d ", vetor[i]);

    printf("\n");

    return 0;
}