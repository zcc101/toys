function producer()
  while true do
    local x = io.read()
    send(x)
  end
end

function consumer()
  while true do
    local x = receive()
    io.write(x, "\n")
  end
end

function send(x)
  coroutine.yield(x)
end

function receive()
  local s, v = coroutine.resume(producer)
  return v
end

producer = coroutine.create(producer)
consumer()