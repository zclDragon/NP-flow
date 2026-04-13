"use client";

import { ArrowLeftIcon } from "lucide-react";
import { useRouter } from "next/navigation";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useI18n } from "@/core/i18n/hooks";

export function BuildSkillPage() {
  const { t } = useI18n();
  const router = useRouter();

  const handleBack = () => {
    router.push("/workspace/data-skill-builder");
  };

  return (
    <div className="flex size-full flex-col">
      <div className="flex items-center justify-between border-b px-6 py-4">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={handleBack}>
            <ArrowLeftIcon className="h-4 w-4" />
          </Button>
          <div>
            <h1 className="text-xl font-semibold">{t.dataSkillBuilder.postgresSkillTitle}</h1>
            <p className="text-muted-foreground mt-0.5 text-sm">
              {t.dataSkillBuilder.postgresSkillDescription}
            </p>
          </div>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-6">
        <Card>
          <CardHeader>
            <CardTitle>postgreSQL源 Skill</CardTitle>
            <CardDescription>
              这里可以连接 PostgreSQL 数据库，创建自定义数据处理 Skill
            </CardDescription>
          </CardHeader>
          <CardContent>
            <p className="text-muted-foreground">
              PostgreSQL Skill 功能开发中...
            </p>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
