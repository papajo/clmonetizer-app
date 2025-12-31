"use client"

import { useState } from "react"
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

    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            url: "",
        },
    })

    async function onSubmit(values: z.infer<typeof formSchema>) {
        setLoading(true)
        setError(null)
        try {
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const requestBody = { url: values.url }
            
            console.log("Sending scrape request:", { apiUrl: `${apiUrl}/api/scrape`, body: requestBody })
            
            const response = await fetch(`${apiUrl}/api/scrape`, {
                method: "POST",
                headers: { 
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                },
                body: JSON.stringify(requestBody)
            })

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
        } catch (error) {
            console.error("Scrape error:", error)
            setError(error instanceof Error ? error.message : "Failed to start scraping job")
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
                    <CardDescription>Enter a Craigslist category URL to start finding deals.</CardDescription>
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
                        <div className="space-y-2">
                            <div className="flex items-center gap-2">
                                <Badge variant="default">Active</Badge>
                                <span className="text-sm text-muted-foreground">
                                    Scraping job started in the background
                                </span>
                            </div>
                            <div className="mt-4 p-3 bg-muted rounded-md">
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
                            <p className="text-xs text-muted-foreground mt-2">
                                The scraping job is running in the background. Check the dashboard for new listings and opportunities.
                            </p>
                        </div>
                    </CardContent>
                </Card>
            )}
        </div>
    )
}
