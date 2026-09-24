fun calculate(x: Int, y: Int) {
    val factor = 2
    val enabled = true
    val result = x + y * factor
    println("result=$result") // Set breakpoint here (line 5)
    println("enabled=$enabled")
}

fun main() {
    calculate(10, 7)
}
