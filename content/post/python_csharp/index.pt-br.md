+++ title = "Estudando C# a partir do Python" 
description = "Estudando C# a partir do Python com a ajuda da IA" 
date = "2025-03-08" 
draft = false 
toc = false 
tags = ["python", "csharp"] 
categories = ["python", "csharp"] 
image = "banner.png" 
author = "Fabio M. Lopes" 
+++

### Código C#, comparando com o Python, e explicando os conceitos principais do C#.
```python
import time

cache = {0:0, 1:1}
calls = 0
cache_hits = 0

def fib(n: int) -> int:
    global calls, cache_hits
    if n in cache:
        cache_hits += 1
        return cache[n]
    else:
        calls += 1
        cache[n] = fib(n-1) + fib(n-2)
        return cache[n]

if __name__ == '__main__':
    n = 500

    start_time = time.perf_counter()
    result = fib(n)
    end_time = time.perf_counter()

    elapsed_time_ms = (end_time - start_time) * 1000

    print(f'{result}')
    print(f'{calls} chamadas de função e {cache_hits} acertos de cache.')
    print(f"Tempo decorrido: {elapsed_time_ms:.4f} ms")
```

### Tradução para C# (com Explicações):
```c#
using System;
using System.Collections.Generic;
using System.Diagnostics;

public class Fibonacci
{
    private static Dictionary<int, long> cache = new Dictionary<int, long> { { 0, 0 }, { 1, 1 } };
    private static long calls = 0;
    private static long cacheHits = 0;

    public static long Fib(int n)
    {
        if (cache.ContainsKey(n))
        {
            cacheHits++;
            return cache[n];
        }
        else
        {
            calls++;
            cache[n] = Fib(n - 1) + Fib(n - 2);
            return cache[n];
        }
    }

    public static void Main(string[] args)
    {
        int n = 500;

        Stopwatch stopwatch = new Stopwatch();
        stopwatch.Start();

        long result = Fib(n);

        stopwatch.Stop();
        double elapsedTimeMs = stopwatch.Elapsed.TotalMilliseconds;

        Console.WriteLine(result);
        Console.WriteLine($"{calls} chamadas de função e {cacheHits} acertos de cache.");
        Console.WriteLine($"Tempo decorrido: {elapsedTimeMs:F4} ms");
    }
}
```

### Conceitos Chave do C#:
 * Namespaces (using System;, etc.):
   * Pense em namespaces como módulos Python. Eles organizam classes e funções relacionadas.
   * using System; importa o namespace System, que contém classes fundamentais como Console.
   * using System.Collections.Generic; importa o namespace de coleções genéricas (para Dictionary).
   * using System.Diagnostics; importa classes para depuração e medição de desempenho (como Stopwatch).
 * Classes (public class Fibonacci):
   * C# é orientado a objetos, então o código é organizado em classes. Uma classe é como um modelo para criar objetos.
   * public significa que a classe é acessível de qualquer lugar.
   * Fibonacci é o nome da nossa classe.
 * Membros Estáticos (private static ...):
   * static significa que o membro (variável ou método) pertence à classe em si, não a instâncias da classe.
   * private significa que o membro só é acessível dentro da classe Fibonacci.
   * Dictionary<int, long> cache: Este é um dicionário (como o dicionário do Python) que armazena chaves inteiras e valores inteiros longos.
   * long calls: Uma variável para contar chamadas de função.
   * long cacheHits: Uma variável para contar acertos de cache.
   * public static long Fib(int n): Esta é a função Fibonacci.
 * Tipos de Dados (int, long, double):
   * C# é estaticamente tipado, então você deve especificar o tipo de dados das variáveis.
   * int: Inteiro (número inteiro).
   * long: Inteiro longo (intervalo maior que int).
   * double: Número de ponto flutuante de precisão dupla (para valores decimais).
   * Dictionary<int, long>: Um dicionário genérico onde as chaves são inteiros e os valores são inteiros longos.
 * Métodos (public static long Fib(int n)):
   * Métodos são como funções Python.
   * public static long Fib(int n):
     * public: Acessível de qualquer lugar.
     * static: Pertence à classe.
     * long: O tipo de retorno do método (ele retorna um inteiro longo).
     * Fib: O nome do método.
     * int n: O parâmetro (entrada) para o método (um inteiro).
 * Fluxo de Controle (if, else):
   * Semelhante ao Python, if e else são usados para execução condicional.
   * cache.ContainsKey(n): Verifica se o dicionário cache contém a chave n.
 * Dicionários (Dictionary<int, long>):
   * Dictionary do C# é equivalente ao dicionário do Python.
   * cache[n]: Acessa o valor associado à chave n.
   * cache.ContainsKey(n): Verifica se uma chave existe.
   * new Dictionary<int, long> { { 0, 0 }, { 1, 1 } }: Inicializa o dicionário com pares chave-valor.
 * Classe Stopwatch:
   * A classe Stopwatch é usada para medir o tempo decorrido.
   * stopwatch.Start(): Inicia o cronômetro.
   * stopwatch.Stop(): Para o cronômetro.
   * stopwatch.Elapsed.TotalMilliseconds: Obtém o tempo decorrido em milissegundos.
 * Console.WriteLine():
   * Usado para exibir texto no console.
   * Interpolação de string ($"{variable}") é usada para incorporar valores de variáveis em strings.
   * :F4 é usado para formatar o tempo decorrido para 4 casas decimais.
 * Método Main:
   * O método Main é o ponto de entrada do programa C#.
   * public static void Main(string[] args):
     * public static: Acessível de qualquer lugar e pertence à classe.
     * void: O método não retorna um valor.
     * string[] args: Um array de argumentos de linha de comando (não estamos usando aqui).

### Principais Diferenças do Python:
 * Tipagem Estática: C# requer declarações de tipo de dados explícitas.
 * Classes e Objetos: C# é mais fortemente orientado a objetos.
 * Namespaces: C# usa namespaces para organização de código.
 * Compilação: O código C# é compilado em código executável antes de ser executado.
 * Sintaxe Explícita: C# tem uma sintaxe mais explícita com chaves ({}) para definir blocos de código.
