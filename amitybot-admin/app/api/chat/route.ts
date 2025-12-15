import Groq from 'groq-sdk'
import { NextResponse } from 'next/server'

const groq = new Groq({
    apiKey: process.env.GROQ_API_KEY!,
})

export async function POST(req: Request) {
    try {
        const body = await req.json()
        const messages = body.messages || []

        const groqMessages = messages.map((msg: any) => ({
            role: msg.role,
            content: msg.content,
        }))

        const chatCompletion = await groq.chat.completions.create({
            messages: groqMessages,
            model: 'mixtral-8x7b-32768',
        })

        const reply = chatCompletion.choices?.[0]?.message?.content || ''

        return NextResponse.json({ role: 'assistant', content: reply })
    } catch (err: any) {
        console.error('Chat error:', err)
        return NextResponse.json({ error: 'Chat failed' }, { status: 500 })
    }
}
