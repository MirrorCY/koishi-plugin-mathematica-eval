import { Context, Schema, h } from 'koishi'

export const name = 'mathematica-eval'

export interface Config {
  token: string
  host: string
  timeout: number
}

interface Response {
  pngs: string[]
}

export const Config: Schema<Config> = Schema.object({
  token: Schema.string().description('42 的狐务器 token，在 [这里](https://forum.koishi.xyz/t/topic/6278) 获取'),
  host: Schema.string().description('狐务器地址').default('http://106.55.149.60:4245/evaluate/'),
  timeout: Schema.number().description('等待服务器响应的时间').default(600000),
})

export function apply(ctx: Context, config: Config) {
  const cmd = ctx.command(`mathematica-eval <code:text>`, 'Mathematica 自然语言交互')
    .example('== -s (114514+114514)*(11-4+5/1-4)+(114*514+(114*51*4+(1145*(1+4)+11-4+5+1-4)))')
    .alias('==')
    .option('timeout', '-t <timeout> 最大执行时间（秒），默认为 10，最大 60', { fallback: 10 })
    .option('step', '-s 尝试展现每一步的计算过程')
    .action(async ({ session, options }, input: string) => {
      if (!input) session.execute('help mathematica-eval')
      session.send('正在执行，不排队的话大约需要 28 秒，请稍候...')
      const data = {
        code: input,
        timeout: options.timeout,
        step: options.step ? true : false,
      }
      const res: Response = await ctx.http.post(config.host, data, { headers: { Authorization: config.token }, timeout: config.timeout })
      const message = h('message')
      if (res.pngs.length > 0) {
        for (const png of res.pngs) {
          message.children.push(h.image(png))
        }
        return message
      }
      else return '执行失败'
    })
}
