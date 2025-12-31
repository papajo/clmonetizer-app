import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Search, TrendingUp, Users, ArrowRight } from "lucide-react"

export default function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-b from-zinc-50 to-white dark:from-black dark:to-zinc-950">
      <main className="container mx-auto px-4 py-16">
        <div className="flex flex-col items-center gap-8 text-center">
          <div className="space-y-4">
            <h1 className="text-5xl font-bold tracking-tight text-black dark:text-zinc-50 sm:text-6xl">
              CL Monetizer
            </h1>
            <p className="max-w-2xl text-xl text-zinc-600 dark:text-zinc-400">
              Automatically discover arbitrage opportunities on Craigslist using AI-powered analysis
            </p>
          </div>

          <div className="flex gap-4">
            <Button asChild size="lg">
              <Link href="/dashboard">
                Go to Dashboard
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
            <Button asChild variant="outline" size="lg">
              <Link href="/dashboard/scraper">
                Start Scraping
              </Link>
            </Button>
          </div>

          <div className="mt-12 grid gap-6 md:grid-cols-3 w-full max-w-4xl">
            <Card>
              <CardHeader>
                <Search className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Smart Scraping</CardTitle>
                <CardDescription>
                  Automatically scrape Craigslist categories and extract listing details
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <TrendingUp className="h-8 w-8 text-primary mb-2" />
                <CardTitle>AI Analysis</CardTitle>
                <CardDescription>
                  AI-powered analysis identifies profitable arbitrage opportunities
                </CardDescription>
              </CardHeader>
            </Card>

            <Card>
              <CardHeader>
                <Users className="h-8 w-8 text-primary mb-2" />
                <CardTitle>Lead Generation</CardTitle>
                <CardDescription>
                  Discover wanted ads and service opportunities automatically
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </main>
    </div>
  )
}
