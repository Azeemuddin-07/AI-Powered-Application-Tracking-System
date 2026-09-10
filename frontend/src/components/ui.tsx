import type { ButtonHTMLAttributes, InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'
import { LoaderCircle } from 'lucide-react'

export function Button({ children, className = '', variant = 'primary', ...props }: ButtonHTMLAttributes<HTMLButtonElement> & { variant?: 'primary'|'secondary'|'danger' }) { return <button className={`btn btn-${variant} ${className}`} {...props}>{children}</button> }
export function Input({ label, error, ...props }: InputHTMLAttributes<HTMLInputElement> & {label?: string; error?: string}) { return <label className="field">{label && <span>{label}</span>}<input {...props}/>{error && <small className="error">{error}</small>}</label> }
export function Textarea({ label, ...props }: TextareaHTMLAttributes<HTMLTextAreaElement> & {label:string}) { return <label className="field"><span>{label}</span><textarea {...props}/></label> }
export function Loader() { return <div className="loader"><LoaderCircle aria-label="Loading"/> Loading…</div> }
export function EmptyState({ title, description, action }: {title:string; description:string; action?:ReactNode}) { return <div className="empty"><h3>{title}</h3><p>{description}</p>{action}</div> }
export function StatusBadge({ status }: {status:string}) { return <span className={`status status-${status.replace('_','-')}`}>{status.replaceAll('_',' ')}</span> }
export function Stat({ label, value }: {label:string; value:number|string}) { return <article className="stat"><p>{label}</p><strong>{value}</strong></article> }
export function Pagination({ page, setPage, hasNext }: {page:number; setPage:(p:number)=>void; hasNext:boolean}) { return <div className="pagination"><Button variant="secondary" disabled={page===1} onClick={()=>setPage(page-1)}>Previous</Button><span>Page {page}</span><Button variant="secondary" disabled={!hasNext} onClick={()=>setPage(page+1)}>Next</Button></div> }
