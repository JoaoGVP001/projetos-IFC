export function formatPhone(value: string): string {
  // Remove tudo que não é dígito
  const cleaned = value.replace(/\D/g, "")

  // Aplica a máscara (XX) XXXXX-XXXX
  if (cleaned.length <= 10) {
    return cleaned.replace(/(\d{2})(\d{4})(\d{0,4})/, "($1) $2-$3")
  } else {
    return cleaned.replace(/(\d{2})(\d{5})(\d{0,4})/, "($1) $2-$3")
  }
}

export function formatCNPJ(value: string): string {
  // Remove tudo que não é dígito
  const cleaned = value.replace(/\D/g, "")

  // Aplica a máscara XX.XXX.XXX/XXXX-XX
  return cleaned.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{0,2})/, "$1.$2.$3/$4-$5")
}

export function validateCNPJ(cnpj: string): boolean {
  const cleaned = cnpj.replace(/\D/g, "")

  if (cleaned.length !== 14) return false

  // Validação básica de CNPJ
  if (/^(\d)\1+$/.test(cleaned)) return false

  // Algoritmo de validação do CNPJ
  let sum = 0
  let weight = 2

  for (let i = 11; i >= 0; i--) {
    sum += Number.parseInt(cleaned.charAt(i)) * weight
    weight = weight === 9 ? 2 : weight + 1
  }

  const remainder = sum % 11
  const digit1 = remainder < 2 ? 0 : 11 - remainder

  if (Number.parseInt(cleaned.charAt(12)) !== digit1) return false

  sum = 0
  weight = 2

  for (let i = 12; i >= 0; i--) {
    sum += Number.parseInt(cleaned.charAt(i)) * weight
    weight = weight === 9 ? 2 : weight + 1
  }

  const remainder2 = sum % 11
  const digit2 = remainder2 < 2 ? 0 : 11 - remainder2

  return Number.parseInt(cleaned.charAt(13)) === digit2
}

export function validatePhone(phone: string): boolean {
  const cleaned = phone.replace(/\D/g, "")
  return cleaned.length >= 10 && cleaned.length <= 11
}
