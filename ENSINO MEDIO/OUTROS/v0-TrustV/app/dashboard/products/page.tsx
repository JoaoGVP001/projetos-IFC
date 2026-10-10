import { redirect } from "next/navigation"
import { createClient } from "@/lib/supabase/server"
import { ProductsList } from "@/components/products/products-list"
import { AuthGuard } from "@/components/auth/auth-guard"

export default async function ProductsPage() {
  const supabase = await createClient()

  const {
    data: { user },
  } = await supabase.auth.getUser()

  if (!user) {
    redirect("/auth/login")
  }

  return (
    <AuthGuard requiredRole={["admin", "seller"]}>
      <div className="container mx-auto py-6 px-4">
        <div className="flex justify-between items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Produtos</h1>
            <p className="text-gray-600 mt-1">Gerencie o catálogo de produtos da sua empresa</p>
          </div>
        </div>
        <ProductsList />
      </div>
    </AuthGuard>
  )
}
