'use client'

import { cn } from 'lib/utils'
import React from 'react'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> { }

export const Input = ({ className, ...props }: InputProps) => {
    return (
        <input
            className={cn('border rounded p-2 w-full', className)}
            {...props}
        />
    )
}
