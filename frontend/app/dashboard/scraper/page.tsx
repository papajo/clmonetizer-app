"use client"

import { useState, useEffect } from "react"
import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"
import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, Loader2, AlertCircle } from "lucide-react"

const formSchema = z.object({
    url: z.string().url({
        message: "Please enter a valid URL.",
    }),
})

export default function ScraperPage() {
    const [loading, setLoading] = useState(false)
    const [lastScrape, setLastScrape] = useState<any>(null)
    const [error, setError] = useState<string | null>(null)
    const [listingsCount, setListingsCount] = useState<number | null>(null)

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            url: "",
        },
    })

    async function checkListingsCount() {
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const response = await fetch(`${apiUrl}/api/stats`)
            if (response.ok) {
                const data = await response.json()
                setListingsCount(data.total_listings)
                console.log("Database stats:", data)
            }
        } catch (err) {
            console.error("Error checking listings count:", err)
        }
    }

    // Check listings count on mount
    useEffect(() => {
        checkListingsCount()
    }, [])

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setLoading(true)
        setError(null)
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const requestBody = { url: values.url }
            
            console.log("Sending scrape request:", { apiUrl: `${apiUrl}/api/scrape`, body: requestBody })
            
            // First check if backend is reachable
            try {
                const healthCheck = await fetch(`${apiUrl}/health`, { 
                    method: "GET",
                    signal: AbortSignal.timeout(3000) // 3 second timeout for health check
                })
                if (!healthCheck.ok) {
                    throw new Error("Backend server is not responding properly")
                }
            } catch (healthError) {
                throw new Error("Cannot connect to backend server. Please ensure the backend is running on " + apiUrl)
            }
            
            // Add timeout to prevent hanging
            const controller = new AbortController()
            const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
            
            const response = await fetch(`${apiUrl}/api/scrape`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(requestBody),
                signal: controller.signal
            })
            
            clearTimeout(timeoutId)

            if (!response.ok) {
                let errorMessage = `Failed to start scrape: ${response.statusText}`
                try {
                    const errorData = await response.json()
                    // Handle FastAPI validation errors
                    if (errorData.detail) {
                        if (Array.isArray(errorData.detail)) {
                            // Multiple validation errors
                            errorMessage = errorData.detail.map((err: any) => 
                                `${err.loc?.join('.')}: ${err.msg}`
                            ).join(', ')
                        } else if (typeof errorData.detail === 'string') {
                            errorMessage = errorData.detail
                        } else {
                            errorMessage = JSON.stringify(errorData.detail)
                        }
                    }
                } catch (e) {
                    // If JSON parsing fails, use the status text
                    console.error("Error parsing error response:", e)
                }
                throw new Error(errorMessage)
            }

            const data = await response.json()
            setLastScrape(data)
            form.reset()
            
            // Check for existing listings periodically
            const checkInterval = setInterval(() => {
                checkListingsCount()
            }, 5000) // Check every 5 seconds
            
            // Stop checking after 2 minutes
            setTimeout(() => {
                clearInterval(checkInterval)
            }, 120000)
        } catch (error) {
            console.error("Scrape error:", error)
            if (error instanceof Error) {
                if (error.name === 'AbortError') {
                    setError("Request timed out. Please check if the backend server is running.")
                } else {
                    setError(error.message)
                }
            } else {
                setError("Failed to start scraping job")
            }
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="flex flex-col gap-6">
            <h1 className="text-3xl font-bold tracking-tight">Scraper Configuration</h1>

            <Card className="w-full max-w-2xl">
                <CardHeader>
                    <CardTitle>Start New Scrape Job</CardTitle>
                    <CardDescription>
                        Enter a Craigslist category URL to start finding deals. 
                        <br />
                        <strong>Tip:</strong> Try scraping the "free" section (e.g., https://[city].craigslist.org/search/sss?query=free) for items you can resell for 100% profit!
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    <Form {...form}>
                        <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
                            <FormField
                                control={form.control}
                                name="url"
                                render={({ field }) => (
                                    <FormItem>
                                        <FormLabel>Category URL</FormLabel>
                                        <FormControl>
                                            <Input placeholder="https://newyork.craigslist.org/search/cto" {...field} />
                                        </FormControl>
                                        <FormDescription>
                                            Paste the full URL from your browser address bar.
                                        </FormDescription>
                                        <FormMessage />
                                    </FormItem>
                                )}
                            />
                            <Button type="submit" disabled={loading}>
                                {loading ? (
                                    <>
                                        <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                                        Starting...
                                    </>
                                ) : (
                                    "Start Scraper"
                                )}
                            </Button>
                        </form>
                    </Form>
                </CardContent>
            </Card>

            {error && (
                <Card className="w-full max-w-2xl border-destructive">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2 text-destructive">
                            <AlertCircle className="h-5 w-5" />
                            Error
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <p className="text-sm text-destructive">{error}</p>
                    </CardContent>
                </Card>
            )}

            {lastScrape && (
                <Card className="w-full max-w-2xl border-green-500">
                    <CardHeader>
                        <CardTitle className="flex items-center gap-2">
                            <CheckCircle2 className="h-5 w-5 text-green-500" />
                            Job Started Successfully
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="space-y-4">
                            <div className="flex items-center gap-2">
                                <Badge variant="default">Active</Badge>
                                <span className="text-sm text-muted-foreground">
                                    Scraping job started in the background
                                </span>
                            </div>
                            <div className="p-3 bg-muted rounded-md">
                                <p className="text-sm font-medium mb-1">URL:</p>
                                <a
                                    href={lastScrape.url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="text-sm text-primary hover:underline break-all"
                                >
                                    {lastScrape.url}
                                </a>
                            </div>
                            <div className="flex gap-2 pt-2">
                                <Button asChild variant="outline" size="sm">
                                    <a href="/dashboard/listings">
                                        View Listings
                                    </a>
                                </Button>
                                <Button asChild variant="outline" size="sm">
                                    <a href="/dashboard">
                                        Go to Dashboard
                                    </a>
                                </Button>
                            </div>
                            <div className="p-3 bg-blue-50 dark:bg-blue-950 rounded-md border border-blue-200 dark:border-blue-800">
                                <p className="text-sm text-blue-900 dark:text-blue-100 mb-2">
                                    <strong>Note:</strong> The scraping job is running in the background. This may take a few minutes depending on the number of listings.
                                </p>
                                <div className="space-y-1">
                                    {listingsCount !== null ? (
                                        <>
                                            <p className="text-sm text-blue-900 dark:text-blue-100 font-semibold">
                                                ✅ Current listings in database: <strong className="text-lg">{listingsCount}</strong>
                                            </p>
                                            {listingsCount > 0 ? (
                                                <p className="text-xs text-blue-700 dark:text-blue-300">
                                                    Listings are being saved! Click <a href="/dashboard/listings" className="underline font-medium">View Listings</a> above to see them.
                                                </p>
                                            ) : (
                                                <p className="text-xs text-blue-700 dark:text-blue-300 italic">
                                                    No listings found yet. The scraper may still be running, or no listings were found on the page. Check backend logs for details.
                                                </p>
                                            )}
                                        </>
                                    ) : (
                                        <p className="text-sm text-blue-900 dark:text-blue-100">
                                            Checking database...
                                        </p>
                                    )}
                                    <p className="text-xs text-blue-700 dark:text-blue-300 mt-2">
                                        💡 <strong>Tip:</strong> The scraper runs in the background. Results appear on the <a href="/dashboard/listings" className="underline font-medium">Listings page</a> as they're discovered. Check backend server console for detailed progress logs.
                                    </p>
                                </div>
                            </div>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
