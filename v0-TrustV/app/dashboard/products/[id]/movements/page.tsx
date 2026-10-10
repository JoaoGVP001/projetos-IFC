import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { ProductMovements } from "@/components/movements/product-movements"
import { AuthGuard } from "@/components/auth/auth-guard"

interface ProductMovementsPageProps {
  params: Promise<{ id: string }>
}

export default async function ProductMovementsPage({ params }: ProductMovementsPageProps) {
  const { id } = await params
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  // Buscar dados do produto
  const { data: product, error } = await supabase
    .from("products")
    .select("id, name, sku, current_stock, unit_of_measure")
    .eq("id", id)
    .single()

  if (error || !product) {
    redirect("/dashboard/products")
  }

  return (
    <AuthGuard requiredRole={["admin", "seller", "accountant"]}>
      <div className="container mx-auto py-6 px-4">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900">Histórico de Movimentações</h1>
          <p className="text-gray-600 mt-1">
            {product.name} - SKU: {product.sku}
          </p>
          <p className="text-sm text-gray-500">
            Estoque atual: {product.current_stock} {product.unit_of_measure}
          </p>
        </div>
        <ProductMovements productId={id} />
      </div>
    </AuthGuard>
  )
}
