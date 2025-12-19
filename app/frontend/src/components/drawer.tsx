import cn from 'classnames'
import '../styles/index.scss';

interface DrawerProps {
  anchor?: "left" | "right"
  isOpen?: boolean
  onClose?: () => void
  children: React.ReactNode
}
export default function Drawer({ anchor = "left", isOpen = false, onClose = () => null, children }: DrawerProps) {
  const css = cn("drawer", anchor === "right" ? "drawer--right" : "", isOpen ? "drawer--open" : "")
  return (
    <div className={css}>
      <button className='fr-btn fr-btn--close' title="close" onClick={onClose}>Close</button>
      {children}
    </div>
  )
}