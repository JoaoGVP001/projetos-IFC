"use client"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { InventoryReport } from "./inventory-report"
import { MovementsReport } from "./movements-report"
import { FiscalReport } from "./fiscal-report"
import { FinancialReport } from "./financial-report"
import { Package, ArrowUpDown, FileText, DollarSign } from "lucide-react"

export function ReportsOverview() {
  return (
    <div className="space-y-6">
      <Tabs defaultValue="inventory" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="inventory" className="flex items-center gap-2">
            <Package className="h-4 w-4" />
            Estoque
          </TabsTrigger>
          <TabsTrigger value="movements" className="flex items-center gap-2">
            <ArrowUpDown className="h-4 w-4" />
            Movimentações
          </TabsTrigger>
          <TabsTrigger value="fiscal" className="flex items-center gap-2">
            <FileText className="h-4 w-4" />
            Fiscal
          </TabsTrigger>
          <TabsTrigger value="financial" className="flex items-center gap-2">
            <DollarSign className="h-4 w-4" />
            Financeiro
          </TabsTrigger>
        </TabsList>

        <TabsContent value="inventory" className="space-y-6">
          <InventoryReport />
        </TabsContent>

        <TabsContent value="movements" className="space-y-6">
          <MovementsReport />
        </TabsContent>

        <TabsContent value="fiscal" className="space-y-6">
          <FiscalReport />
        </TabsContent>

        <TabsContent value="financial" className="space-y-6">
          <FinancialReport />
        </TabsContent>
      </Tabs>
    </div>
  )
}
