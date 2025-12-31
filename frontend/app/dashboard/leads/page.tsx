"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"
import { ExternalLink } from "lucide-react"

interface Lead {
    id: number
    title: string
    url: string
    lead_type: string
    contact_info: string | null
    status: string
    created_at: string
}

export default function LeadsPage() {
    const [leads, setLeads] = useState<Lead[]>([])
    const [loading, setLoading] = useState(true)
    const [error, setError] = useState<string | null>(null)

    useEffect(() => {
        fetchLeads()
    }, [])

    async function fetchLeads() {
        try {
            setLoading(true)
            const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
            const response = await fetch(`${apiUrl}/api/leads`)
            
            if (!response.ok) {
                throw new Error(`Failed to fetch leads: ${response.statusText}`)
            }

            const data = await response.json()
            setLeads(data)
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load leads")
            console.error("Error fetching leads:", err)
        } finally {
            setLoading(false)
        }
    }

    const getStatusBadgeVariant = (status: string) => {
        switch (status) {
            case "new":
                return "default"
            case "contacted":
                return "secondary"
            case "sold":
                return "outline"
            default:
                return "default"
        }
    }

    const getTypeBadgeVariant = (type: string) => {
        switch (type) {
            case "wanted":
                return "destructive"
            case "service_target":
                return "default"
            default:
                return "secondary"
        }
    }

    return (
        <div className="flex flex-col gap-6">
            <div className="flex items-center justify-between">
                <h1 className="text-3xl font-bold tracking-tight">Leads & Opportunities</h1>
                <Badge variant="outline">{leads.length} Total Leads</Badge>
            </div>

            <Card>
                <CardHeader>
                    <CardTitle>Active Leads</CardTitle>
                    <CardDescription>
                        Generated leads from wanted ads and service opportunities
                    </CardDescription>
                </CardHeader>
                <CardContent>
                    {loading ? (
                        <div className="space-y-4">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="flex items-center space-x-4">
                                    <Skeleton className="h-12 w-full" />
                                </div>
                            ))}
                        </div>
                    ) : error ? (
                        <div className="text-center py-8 text-destructive">
                            <p>{error}</p>
                            <button
                                onClick={fetchLeads}
                                className="mt-4 text-sm underline"
                            >
                                Retry
                            </button>
                        </div>
                    ) : leads.length === 0 ? (
                        <div className="text-center py-8 text-muted-foreground">
                            <p>No leads found. Start scraping to generate leads.</p>
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Title</TableHead>
                                    <TableHead>Type</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Contact Info</TableHead>
                                    <TableHead>Created</TableHead>
                                    <TableHead>Actions</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {leads.map((lead) => (
                                    <TableRow key={lead.id}>
                                        <TableCell className="font-medium">
                                            {lead.title || "Untitled"}
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={getTypeBadgeVariant(lead.lead_type)}>
                                                {lead.lead_type}
                                            </Badge>
                                        </TableCell>
                                        <TableCell>
                                            <Badge variant={getStatusBadgeVariant(lead.status)}>
                                                {lead.status}
                                            </Badge>
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {lead.contact_info || "N/A"}
                                        </TableCell>
                                        <TableCell className="text-sm text-muted-foreground">
                                            {new Date(lead.created_at).toLocaleDateString()}
                                        </TableCell>
                                        <TableCell>
                                            {lead.url && (
                                                <a
                                                    href={lead.url}
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

