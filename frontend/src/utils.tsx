export const dateStringToNumber = (dateString: string) => new Date(dateString).getTime()

export const formatDate = (date: Date | string): string => {
  const d = typeof date === "string" ? new Date(date) : date
  return d.toLocaleString("fr-FR", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  })
}

export const formatDuration = (duration: number): string => {
  const d = new Date(duration * 1000)
  return d.toLocaleTimeString("fr-FR", { hour: "numeric", minute: "2-digit", second: "2-digit" })
}