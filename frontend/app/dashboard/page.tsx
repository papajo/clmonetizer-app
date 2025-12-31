"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { DollarSign, Search, Users, TrendingUp } from "lucide-react"
import { Skeleton } from "@/components/ui/skeleton"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Badge } from "@/components/ui/badge"
import { ExternalLink, AlertCircle } from "lucide-react"

interface Stats {
    total_listings: number
    opportunities: number
    total_leads: number
    total_profit_potential: number
    ai_configured?: boolean
}

interface Listing {
    id: number
    title: string
    url: string
    price: number | null
    location: string | null
    is_arbitrage_opportunity: boolean
    profit_potential: number | null
    date_scraped: string
}

export default function DashboardPage() {
    const [stats, setStats] = useState<Stats | null>(null)
    const [opportunities, setOpportunities] = useState<Listing[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchDashboardData()
    }, [])

    async function fetchDashboardData() {
        try {
            setLoading(true)
            setError(null)
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            
            // First check if backend is reachable
            try {
                const healthCheck = await fetch(`${apiUrl}/health`, { 
                    method: "GET",
                    signal: AbortSignal.timeout(3000)
                })
                if (!healthCheck.ok) {
                    throw new Error(`Backend server returned status ${healthCheck.status}`)
                }
            } catch (healthErr) {
                if (healthErr instanceof Error && healthErr.name === 'AbortError') {
                    throw new Error("Backend server is not responding. Make sure it's running on " + apiUrl)
                }
                throw new Error(`Cannot connect to backend: ${healthErr instanceof Error ? healthErr.message : 'Unknown error'}`)
            }
            
            const [statsRes, oppsRes] = await Promise.all([
                fetch(`${apiUrl}/api/stats`, {
                    signal: AbortSignal.timeout(10000)
                }),
                fetch(`${apiUrl}/api/listings/opportunities?limit=5`, {
                    signal: AbortSignal.timeout(10000)
                })
            ])

            if (!statsRes.ok) {
                const errorText = await statsRes.text().catch(() => statsRes.statusText)
                throw new Error(`Failed to fetch stats: ${statsRes.status} ${errorText}`)
            }
            
            if (!oppsRes.ok) {
                const errorText = await oppsRes.text().catch(() => oppsRes.statusText)
                throw new Error(`Failed to fetch opportunities: ${oppsRes.status} ${errorText}`)
            }

            const [statsData, oppsData] = await Promise.all([
                statsRes.json(),
                oppsRes.json()
            ])

            setStats(statsData)
            setOpportunities(oppsData)
        } catch (err) {
            const errorMessage = err instanceof Error 
                ? err.message 
                : "Failed to load dashboard"
            setError(errorMessage)
            console.error("Error fetching dashboard data:", err)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (value: number) => {
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value)
    }

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Dashboard</h1>
                <div className="flex gap-2">
                    <Button onClick={fetchDashboardData} variant="outline" disabled={loading}>
                        {loading ? "Refreshing..." : "Refresh"}
                    </Button>
                    <Button asChild variant="outline">
                        <Link href="/dashboard/scraper">Start New Scrape</Link>
                    </Button>
                </div>
            </div>

            {loading ? (
                <div className="grid gap-4 md:grid-cols-3">
                    {[1, 2, 3].map((i) => (
                        <Card key={i}>
                            <CardHeader>
                                <Skeleton className="h-4 w-24" />
                            </CardHeader>
                            <CardContent>
                                <Skeleton className="h-8 w-32 mb-2" />
                                <Skeleton className="h-3 w-40" />
                            </CardContent>
                        </Card>
                    ))}
                </div>
            ) : error ? (
                <Card>
                    <CardContent className="pt-6">
                        <div className="text-center text-destructive">
                            <p>{error}</p>
                            <Button onClick={fetchDashboardData} variant="outline" className="mt-4">
                                Retry
                            </Button>
                        </div>
                    </CardContent>
                </Card>
            ) : (
                <>
                    {stats && !stats.ai_configured && (
                        <Card className="border-yellow-500 bg-yellow-50 dark:bg-yellow-950">
                            <CardHeader>
                                <CardTitle className="flex items-center gap-2 text-yellow-800 dark:text-yellow-200">
                                    <AlertCircle className="h-5 w-5" />
                                    AI Analysis Not Configured
                                </CardTitle>
                            </CardHeader>
                            <CardContent>
                                <p className="text-sm text-yellow-900 dark:text-yellow-100 mb-4">
                                    OpenAI API key is not configured. Without it, listings cannot be analyzed for arbitrage opportunities.
                                </p>
                                <div className="space-y-2 text-sm text-yellow-800 dark:text-yellow-200">
                                    <p><strong>To fix this:</strong></p>
                                    <ol className="list-decimal list-inside space-y-1 ml-2">
                                        <li>Get your API key from <a href="https://platform.openai.com/account/api-keys" target="_blank" rel="noopener noreferrer" className="underline">OpenAI</a></li>
                                        <li>Set the environment variable: <code className="bg-yellow-100 dark:bg-yellow-900 px-1 rounded">export OPENAI_API_KEY=sk-...</code></li>
                                        <li>Restart the backend server</li>
                                        <li>Re-analyze existing listings using the button below</li>
                                    </ol>
                                </div>
                            </CardContent>
                        </Card>
                    )}
                    <div className="grid gap-4 md:grid-cols-3">
                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    Total Revenue Potential
                                </CardTitle>
                                <DollarSign className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">
                                    {stats ? formatCurrency(stats.total_profit_potential) : "$0"}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                    From {stats?.opportunities || 0} opportunities
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    Total Listings
                                </CardTitle>
                                <Search className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats?.total_listings || 0}</div>
                                <p className="text-xs text-muted-foreground">
                                    {stats?.opportunities || 0} arbitrage opportunities
                                </p>
                            </CardContent>
                        </Card>

                        <Card>
                            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                                <CardTitle className="text-sm font-medium">
                                    Leads Generated
                                </CardTitle>
                                <Users className="h-4 w-4 text-muted-foreground" />
                            </CardHeader>
                            <CardContent>
                                <div className="text-2xl font-bold">{stats?.total_leads || 0}</div>
                                <p className="text-xs text-muted-foreground">
                                    <Link href="/dashboard/leads" className="hover:underline">
                                        View all leads
                                    </Link>
                                </p>
                            </CardContent>
                        </Card>
                    </div>

                    <Card>
                        <CardHeader>
                            <CardTitle>Top Opportunities</CardTitle>
                        </CardHeader>
                        <CardContent>
                            {opportunities.length === 0 ? (
                                <div className="text-center py-8 text-muted-foreground">
                                    <p>
                                        {stats && !stats.ai_configured 
                                            ? "AI analysis is not configured. Set up your OpenAI API key to analyze listings for arbitrage opportunities."
                                            : "No opportunities found yet. Start scraping to discover deals!"
                                        }
                                    </p>
                                    <div className="flex gap-2 justify-center mt-4">
                                        {stats && !stats.ai_configured ? (
                                            <Button asChild variant="outline">
                                                <Link href="/dashboard/settings">Configure API Key</Link>
                                            </Button>
                                        ) : (
                                            <>
                                                <Button asChild>
                                                    <Link href="/dashboard/scraper">Start Scraping</Link>
                                                </Button>
                                                {stats && stats.total_listings > 0 && (
                                                    <Button 
                                                        onClick={async () => {
                                                            try {
                                                                const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/api/listings/reanalyze`, {
                                                                    method: "POST"
                                                                })
                                                                if (response.ok) {
                                                                    const data = await response.json()
                                                                    alert(`Re-analysis started for ${data.count} listings. This may take a few minutes.`)
                                                                    setTimeout(() => fetchDashboardData(), 5000)
                                                                }
                                                            } catch (err) {
                                                                console.error("Error starting re-analysis:", err)
                                                            }
                                                        }}
                                                        variant="outline"
                                                    >
                                                        Re-analyze Existing Listings
                                                    </Button>
                                                )}
                                            </>
                                        )}
                                    </div>
                                </div>
                            ) : (
                                <Table>
                                    <TableHeader>
                                        <TableRow>
                                            <TableHead>Title</TableHead>
                                            <TableHead>Price</TableHead>
                                            <TableHead>Profit Potential</TableHead>
                                            <TableHead>Location</TableHead>
                                            <TableHead>Actions</TableHead>
                                        </TableRow>
                                    </TableHeader>
                                    <TableBody>
                                        {opportunities.map((listing) => (
                                            <TableRow key={listing.id}>
                                                <TableCell className="font-medium">
                                                    {listing.title}
                                                </TableCell>
                                                <TableCell>
                                                    {listing.price ? formatCurrency(listing.price) : "N/A"}
                                                </TableCell>
                                                <TableCell>
                                                    <Badge variant="default" className="gap-1">
                                                        <TrendingUp className="h-3 w-3" />
                                                        {listing.profit_potential ? formatCurrency(listing.profit_potential) : "N/A"}
                                                    </Badge>
                                                </TableCell>
                                                <TableCell className="text-sm text-muted-foreground">
                                                    {listing.location || "N/A"}
                                                </TableCell>
                                                <TableCell>
                                                    {listing.url && (
                                                        <a
                                                            href={listing.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="inline-flex items-center gap-1 text-sm text-primary hover:underline"
                                                        >
                                                            View <ExternalLink className="h-3 w-3" />
                                                        </a>
                                                    )}
                                                </TableCell>
                                            </TableRow>
                                        ))}
                                    </TableBody>
                                </Table>
                            )}
                        </CardContent>
                    </Card>
                </>
            )}
        </div>
    )
}
