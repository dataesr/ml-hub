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
  const d = new Date(0)
  d.setSeconds(duration) // specify value for SECONDS here
  return d.toISOString().substring(11, 19)
}

export const scrollToTop = () => {
  window.scrollTo({
    top: 0,
    behavior: "smooth",
  })
}