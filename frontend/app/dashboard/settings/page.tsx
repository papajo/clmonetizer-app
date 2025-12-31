"use client"

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Separator } from "@/components/ui/separator"

export default function SettingsPage() {
    return (
        <div className="flex flex-col gap-6">
            <h1 className="text-3xl font-bold tracking-tight">Settings</h1>

            <Card>
                <CardHeader>
                    <CardTitle>API Configuration</CardTitle>
                    <CardDescription>
                        Configure API endpoints and connection settings
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="api-url">API URL</Label>
                        <Input
                            id="api-url"
                            placeholder="http://localhost:8000"
                            defaultValue={process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}
                        />
                        <p className="text-sm text-muted-foreground">
                            Backend API endpoint URL
                        </p>
                    </div>
                    <Button>Save Changes</Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>Scraper Settings</CardTitle>
                    <CardDescription>
                        Configure scraping behavior and limits
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="scrape-delay">Scrape Delay (seconds)</Label>
                        <Input
                            id="scrape-delay"
                            type="number"
                            placeholder="2"
                            defaultValue="2"
                        />
                        <p className="text-sm text-muted-foreground">
                            Delay between requests to avoid rate limiting
                        </p>
                    </div>
                    <div className="space-y-2">
                        <Label htmlFor="max-listings">Max Listings Per Scrape</Label>
                        <Input
                            id="max-listings"
                            type="number"
                            placeholder="100"
                            defaultValue="100"
                        />
                        <p className="text-sm text-muted-foreground">
                            Maximum number of listings to scrape per job
                        </p>
                    </div>
                    <Button>Save Changes</Button>
                </CardContent>
            </Card>

            <Card>
                <CardHeader>
                    <CardTitle>AI Analysis Settings</CardTitle>
                    <CardDescription>
                        Configure AI analysis parameters
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                    <div className="space-y-2">
                        <Label htmlFor="min-profit">Minimum Profit Threshold ($)</Label>
                        <Input
                            id="min-profit"
                            type="number"
                            placeholder="50"
                            defaultValue="50"
                        />
                        <p className="text-sm text-muted-foreground">
                            Only flag opportunities with profit potential above this amount
                        </p>
                    </div>
                    <Button>Save Changes</Button>
                </CardContent>
            </Card>
        </div>
    )
}

