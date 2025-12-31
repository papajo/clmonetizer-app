"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { ExternalLink, TrendingUp, RefreshCw } from "lucide-react"

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

export default function ListingsPage() {
    const [listings, setListings] = useState<Listing[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)
    const [filter, setFilter] = useState<"all" | "opportunities">("all")
    const [searchQuery, setSearchQuery] = useState("")

    useEffect(() => {
        fetchListings()
    }, [filter])

    async function fetchListings() {
        try {
            setLoading(true)
            setError(null)
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const endpoint = filter === "opportunities" 
                ? `${apiUrl}/api/listings/opportunities`
                : `${apiUrl}/api/listings`
            
            const response = await fetch(endpoint)
            
            if (!response.ok) {
                throw new Error(`Failed to fetch listings: ${response.statusText}`)
            }

            const data = await response.json()
            setListings(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load listings")
            console.error("Error fetching listings:", err)
        } finally {
            setLoading(false)
        }
    }

    const formatCurrency = (value: number | null) => {
        if (value === null) return "N/A"
        return new Intl.NumberFormat("en-US", {
            style: "currency",
            currency: "USD",
            minimumFractionDigits: 0,
            maximumFractionDigits: 0,
        }).format(value)
    }

    const filteredListings = listings.filter(listing => {
        if (!searchQuery) return true
        const query = searchQuery.toLowerCase()
        return (
            listing.title?.toLowerCase().includes(query) ||
            listing.location?.toLowerCase().includes(query)
        )
    })

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Listings</h1>
                <Button onClick={fetchListings} variant="outline" disabled={loading}>
                    <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
                    Refresh
                </Button>
            </div>

            <div className="flex gap-4 items-center">
                <div className="flex gap-2">
                    <Button
                        variant={filter === "all" ? "default" : "outline"}
                        onClick={() => setFilter("all")}
                    >
                        All Listings
                    </Button>
                    <Button
                        variant={filter === "opportunities" ? "default" : "outline"}
                        onClick={() => setFilter("opportunities")}
                    >
                        Opportunities Only
                    </Button>
                </div>
                <Input
                    placeholder="Search by title or location..."
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    className="max-w-sm"
                />
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>
                        {filter === "opportunities" ? "Arbitrage Opportunities" : "All Listings"}
                    </CardTitle>
                    <CardDescription>
                        {filteredListings.length} {filteredListings.length === 1 ? "listing" : "listings"} found
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="space-y-4">
                            {[1, 2, 3, 4, 5].map((i) => (
                                <div key={i} className="flex items-center space-x-4">
                                    <Skeleton className="h-12 w-full" />
                                </div>
                            ))}
                        </div>
                    ) : error ? (
                        <div className="text-center py-8 text-destructive">
                            <p>{error}</p>
                            <Button onClick={fetchListings} variant="outline" className="mt-4">
                                Retry
                            </Button>
                        </div>
                    ) : filteredListings.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            <p>
                                {searchQuery 
                                    ? "No listings match your search criteria."
                                    : filter === "opportunities"
                                    ? "No arbitrage opportunities found yet. Start scraping to discover deals!"
                                    : "No listings found. Start scraping to collect listings!"
                                }
                            </p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Title</TableHead>
                                    <TableHead>Price</TableHead>
                                    <TableHead>Profit Potential</TableHead>
                                    <TableHead>Location</TableHead>
                                    <TableHead>Scraped</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {filteredListings.map((listing) => (
                                    <TableRow key={listing.id}>
                                        <TableCell className="font-medium">
                                            {listing.title || "Untitled"}
                                        </TableCell>
                                        <TableCell>
                                            {formatCurrency(listing.price)}
                                        </TableCell>
                                        <TableCell>
                                            {listing.is_arbitrage_opportunity && listing.profit_potential ? (
                                                <Badge variant="default" className="gap-1">
                                                    <TrendingUp className="h-3 w-3" />
                                                    {formatCurrency(listing.profit_potential)}
                                                </Badge>
                                            ) : (
                                                <span className="text-sm text-muted-foreground">—</span>
                                            )}
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {listing.location || "N/A"}
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {new Date(listing.date_scraped).toLocaleDateString()}
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
        </div>
    )
}

